from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
import boto3
from models import (
    AgentEvent,
    AgentMetrics,
    AgentEventResponse,
    MetricsResponse,
    DashboardKPI,
    DashboardKPIsResponse,
    EventItem,
    EventsResponse,
    MetricsSeriesResponse,
    SeriesPoint,
    ConversationsResponse,
    ConversationItem,
)
from config import Config

router = APIRouter()

# Search backend helpers
def os_enabled():
    return Config.SEARCH_BACKEND == 'opensearch' and bool(Config.OPENSEARCH_URL)

def get_opensearch_client():
    from opensearchpy import OpenSearch
    auth = None
    if Config.OPENSEARCH_USER and Config.OPENSEARCH_PASS:
        auth = (Config.OPENSEARCH_USER, Config.OPENSEARCH_PASS)
    return OpenSearch(Config.OPENSEARCH_URL, http_auth=auth, verify_certs=False)

# Initialize DynamoDB client
def get_dynamodb_client():
    """Get DynamoDB client using env-configured endpoint if provided."""
    endpoint = Config.DYNAMODB_ENDPOINT.strip() if Config.DYNAMODB_ENDPOINT else None
    if endpoint:
        return boto3.resource(
            'dynamodb',
            region_name=Config.AWS_REGION,
            endpoint_url=endpoint,
            aws_access_key_id=(Config.AWS_ACCESS_KEY_ID or 'dummy'),
            aws_secret_access_key=(Config.AWS_SECRET_ACCESS_KEY or 'dummy'),
        )
    # Default: use AWS if keys are present; otherwise local
    if Config.AWS_ACCESS_KEY_ID and Config.AWS_SECRET_ACCESS_KEY:
        return boto3.resource('dynamodb', region_name=Config.AWS_REGION)
    return boto3.resource(
        'dynamodb',
        region_name=Config.AWS_REGION,
        endpoint_url='http://localhost:8000',
        aws_access_key_id='dummy',
        aws_secret_access_key='dummy',
    )


def _date_only(ts: str) -> str:
    # Expect ISO8601; fall back to first 10 chars
    try:
        return datetime.fromisoformat(ts.replace('Z', '+00:00')).strftime('%Y-%m-%d')
    except Exception:
        return ts[:10]


def _safe_int(val, default=0):
    try:
        return int(val)
    except Exception:
        return default


def _update_metrics_for_event(dynamodb, evt: AgentEvent):
    metrics_table = dynamodb.Table(Config.DYNAMODB_TABLE_METRICS)
    date_str = _date_only(evt.timestamp)
    # Build atomic updates
    update_expr_parts = [
        'ADD total_messages :one',
        'ADD total_tokens_used :tokens',
    ]
    expr_values = {
        ':one': 1,
        ':tokens': _safe_int(evt.token_count or 0),
    }
    # Responses and errors
    if evt.message_type == 'agent_response':
        update_expr_parts.append('ADD total_responses :one')
    if evt.message_type == 'error':
        update_expr_parts.append('ADD total_errors :one')
    # Response time rolling sums
    if evt.response_time_ms is not None:
        update_expr_parts.append('ADD response_time_sum :rt, response_count :one')
        expr_values[':rt'] = _safe_int(evt.response_time_ms)
    # Feedback rolling sums
    if evt.user_feedback is not None:
        update_expr_parts.append('ADD feedback_sum :fs, feedback_count :one')
        expr_values[':fs'] = _safe_int(evt.user_feedback)
    # Unique users via set add if provided
    user_id = None
    if evt.metadata and isinstance(evt.metadata, dict):
        user_id = evt.metadata.get('user_id')
    if user_id:
        update_expr_parts.append('ADD user_ids :uid')
        expr_values[':uid'] = set([str(user_id)])

    # Ensure base attributes exist
    set_defaults = 'SET agent_id = if_not_exists(agent_id, :aid), date = if_not_exists(date, :d)'
    expr_values[':aid'] = evt.agent_id
    expr_values[':d'] = date_str

    update_expression = set_defaults + ' ' + ' '.join(update_expr_parts)
    metrics_table.update_item(
        Key={'agent_id': evt.agent_id, 'date': date_str},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expr_values,
    )

@router.post("/agents/{agent_id}/events", response_model=AgentEventResponse)
async def record_agent_event(agent_id: str, event: AgentEvent):
    """Record an agent event (message, response, error, etc.)"""
    try:
        dynamodb = get_dynamodb_client()
        events_table = dynamodb.Table(Config.DYNAMODB_TABLE_EVENTS)

        # Ensure agent_id matches the URL parameter
        event.agent_id = agent_id

        # Generate unique event ID
        event_id = str(uuid.uuid4())

        # Add to DynamoDB
        trace_id = None
        conversation_id = None
        user_id = None
        if event.metadata and isinstance(event.metadata, dict):
            trace_id = event.metadata.get('trace_id')
            conversation_id = event.metadata.get('conversation_id')
            user_id = event.metadata.get('user_id')

        item = {
            'agent_id': event.agent_id,
            'timestamp': event.timestamp,
            'message_type': event.message_type,
            'content': event.content,
            'metadata': event.metadata,
            'error_details': event.error_details,
            'response_time_ms': event.response_time_ms,
            'token_count': event.token_count,
            'model_used': event.model_used,
            'user_feedback': event.user_feedback,
        }
        if trace_id:
            item['trace_id'] = str(trace_id)
        if conversation_id:
            item['conversation_id'] = str(conversation_id)
        if user_id:
            item['user_id'] = str(user_id)

        events_table.put_item(Item=item)

        # Index into OpenSearch for rich queries
        if os_enabled():
            try:
                os_client = get_opensearch_client()
                doc = dict(item)
                doc['@timestamp'] = event.timestamp
                os_client.index(index=Config.OPENSEARCH_INDEX_EVENTS, document=doc)
            except Exception:
                # Do not fail ingestion if OS is unavailable
                pass

        # Update aggregated metrics for the day
        _update_metrics_for_event(dynamodb, event)

        return AgentEventResponse(
            event_id=event_id,
            status="success",
            message="Event recorded successfully"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record event: {str(e)}")

@router.get("/agents/{agent_id}/metrics", response_model=MetricsResponse)
async def get_agent_metrics(
    agent_id: str,
    days: int = 7,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get aggregated metrics for an agent"""
    try:
        dynamodb = get_dynamodb_client()
        metrics_table = dynamodb.Table(Config.DYNAMODB_TABLE_METRICS)

        # Calculate date range
        if not start_date:
            end_date_obj = datetime.now()
            start_date_obj = end_date_obj - timedelta(days=days)
            start_date = start_date_obj.strftime("%Y-%m-%d")
            if not end_date:
                end_date = end_date_obj.strftime("%Y-%m-%d")

        # Query metrics for the date range
        response = metrics_table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('agent_id').eq(agent_id)
            & boto3.dynamodb.conditions.Key('date').between(start_date, end_date)
        )

        # Aggregate metrics
        total_metrics = AgentMetrics(
            agent_id=agent_id,
            date=f"{start_date}_to_{end_date}"
        )

        for item in response.get('Items', []):
            total_metrics.total_messages += item.get('total_messages', 0)
            total_metrics.total_responses += item.get('total_responses', 0)
            total_metrics.total_errors += item.get('total_errors', 0)
            total_metrics.total_tokens_used += item.get('total_tokens_used', 0)
            # If user_ids set exists, use its length; else use numeric counter if present
            user_ids = item.get('user_ids')
            if isinstance(user_ids, set):
                total_metrics.unique_users += len(user_ids)
            else:
                total_metrics.unique_users += item.get('unique_users', 0)

        # Calculate averages
        items = response.get('Items', [])
        if items:
            # Prefer rolling sums if present
            rt_sum = sum(item.get('response_time_sum', 0) for item in items)
            rt_count = sum(item.get('response_count', 0) for item in items)
            if rt_count > 0:
                total_metrics.average_response_time = rt_sum / rt_count

            fb_sum = sum(item.get('feedback_sum', 0) for item in items)
            fb_count = sum(item.get('feedback_count', 0) for item in items)
            if fb_count > 0:
                total_metrics.average_feedback_score = fb_sum / fb_count

        return MetricsResponse(
            agent_id=agent_id,
            metrics=total_metrics,
            time_range=f"{start_date} to {end_date}"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve metrics: {str(e)}")

@router.get("/agents", response_model=List[str])
async def list_agents():
    """Get list of all agent IDs"""
    try:
        dynamodb = get_dynamodb_client()
        events_table = dynamodb.Table(Config.DYNAMODB_TABLE_EVENTS)

        # Scan for unique agent IDs (not efficient for large datasets, but works for demo)
        response = events_table.scan(
            ProjectionExpression='agent_id'
        )

        agent_ids = set()
        for item in response['Items']:
            agent_ids.add(item['agent_id'])

        return list(agent_ids)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list agents: {str(e)}")


@router.get("/events", response_model=EventsResponse)
async def list_events(
    agent_id: Optional[str] = None,
    message_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
):
    """List events with optional filtering. Uses Query when agent_id provided; otherwise Scan.

    For date filtering, provide start_date/end_date in YYYY-MM-DD; compares on the timestamp prefix.
    """
    try:
        if os_enabled():
            os_client = get_opensearch_client()
            must = []
            if agent_id:
                must.append({"term": {"agent_id": agent_id}})
            if message_type:
                must.append({"term": {"message_type": message_type}})

            time_filter = None
            if start_date and end_date:
                time_filter = {"range": {"timestamp": {"gte": start_date, "lte": end_date + 'T23:59:59Z'}}}
            body = {
                "size": limit,
                "query": {
                    "bool": {
                        "must": must,
                        **({"filter": [time_filter]} if time_filter else {}),
                    }
                },
                "sort": [{"timestamp": {"order": "desc"}}]
            }
            res = os_client.search(index=Config.OPENSEARCH_INDEX_EVENTS, body=body)
            hits = [h.get('_source', {}) for h in res.get('hits', {}).get('hits', [])]
            event_items = []
            for i in hits:
                # Map to EventItem fields
                event_items.append(EventItem(
                    agent_id=i.get('agent_id'),
                    timestamp=i.get('timestamp') or i.get('@timestamp'),
                    message_type=i.get('message_type'),
                    content=i.get('content'),
                    metadata=i.get('metadata'),
                    error_details=i.get('error_details'),
                    response_time_ms=i.get('response_time_ms'),
                    token_count=i.get('token_count'),
                    model_used=i.get('model_used'),
                    user_feedback=i.get('user_feedback'),
                ))
            return EventsResponse(items=event_items, next_key=None)

        dynamodb = get_dynamodb_client()
        events_table = dynamodb.Table(Config.DYNAMODB_TABLE_EVENTS)

        items = []
        if agent_id:
            if not start_date or not end_date:
                # default last 7 days
                end_dt = datetime.now()
                start_dt = end_dt - timedelta(days=7)
                start_date = start_dt.strftime("%Y-%m-%d")
                end_date = end_dt.strftime("%Y-%m-%d")
            # Build KeyCondition: timestamp between start and end by prefix
            # Store timestamps as ISO; we can use full range if you pass full ISO times.
            resp = events_table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key('agent_id').eq(agent_id)
                & boto3.dynamodb.conditions.Key('timestamp').between(start_date, end_date + 'T23:59:59Z'),
                Limit=limit,
                ScanIndexForward=False,
            )
            items = resp.get('Items', [])
        else:
            # Fallback scan with filters
            scan_kwargs = {"Limit": limit}
            filter_expr = None
            from boto3.dynamodb.conditions import Attr
            if message_type:
                filter_expr = Attr('message_type').eq(message_type)
            if start_date and end_date:
                date_filter = Attr('timestamp').between(start_date, end_date + 'T23:59:59Z')
                filter_expr = date_filter if filter_expr is None else (filter_expr & date_filter)
            if filter_expr is not None:
                scan_kwargs['FilterExpression'] = filter_expr
            resp = events_table.scan(**scan_kwargs)
            items = resp.get('Items', [])

        # Map to response model shape
        event_items = [EventItem(**i) for i in items]
        return EventsResponse(items=event_items, next_key=None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list events: {str(e)}")


@router.get("/dashboard/kpis", response_model=DashboardKPIsResponse)
async def dashboard_kpis(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    agents: Optional[str] = None,  # comma-separated
):
    """Aggregate KPIs across agents and dates.

    - agents: optional comma-separated list to restrict aggregation
    - start_date/end_date: YYYY-MM-DD; defaults to last 7 days
    """
    try:
        dynamodb = get_dynamodb_client()
        metrics_table = dynamodb.Table(Config.DYNAMODB_TABLE_METRICS)

        if not start_date or not end_date:
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=7)
            start_date = start_date or start_dt.strftime("%Y-%m-%d")
            end_date = end_date or end_dt.strftime("%Y-%m-%d")

        agent_list = [a for a in (agents.split(',') if agents else []) if a]

        totals = {
            'calls': 0,
            'errors': 0,
            'tokens': 0,
            'rt_sum': 0,
            'rt_count': 0,
        }

        # If agents provided, query per agent; else scan the date range
        if agent_list:
            for aid in agent_list:
                resp = metrics_table.query(
                    KeyConditionExpression=boto3.dynamodb.conditions.Key('agent_id').eq(aid)
                    & boto3.dynamodb.conditions.Key('date').between(start_date, end_date)
                )
                for it in resp.get('Items', []):
                    totals['calls'] += it.get('total_messages', 0)
                    totals['errors'] += it.get('total_errors', 0)
                    totals['tokens'] += it.get('total_tokens_used', 0)
                    totals['rt_sum'] += it.get('response_time_sum', 0)
                    totals['rt_count'] += it.get('response_count', 0)
        else:
            # Scan with date filter
            from boto3.dynamodb.conditions import Attr
            resp = metrics_table.scan(
                FilterExpression=Attr('date').between(start_date, end_date)
            )
            for it in resp.get('Items', []):
                totals['calls'] += it.get('total_messages', 0)
                totals['errors'] += it.get('total_errors', 0)
                totals['tokens'] += it.get('total_tokens_used', 0)
                totals['rt_sum'] += it.get('response_time_sum', 0)
                totals['rt_count'] += it.get('response_count', 0)

        avg_latency = (totals['rt_sum'] / totals['rt_count']) if totals['rt_count'] > 0 else 0.0

        # For demo, compute naive changes as zeros
        kpis = [
            DashboardKPI(title='LLM Calls', value=float(totals['calls']), change=0.0, changeType='increase', description='Total API calls'),
            DashboardKPI(title='Error Rate', value=float((totals['errors'] / totals['calls'] * 100) if totals['calls'] else 0.0), change=0.0, changeType='decrease', description='Failed requests %'),
            DashboardKPI(title='Avg Latency (ms)', value=float(avg_latency), change=0.0, changeType='decrease', description='Mean response time'),
            DashboardKPI(title='Tokens Used', value=float(totals['tokens']), change=0.0, changeType='increase', description='Total tokens processed'),
        ]

        return DashboardKPIsResponse(
            start_date=start_date,
            end_date=end_date,
            agents=agent_list or None,
            kpis=kpis,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compute KPIs: {str(e)}")


@router.get("/metrics/series", response_model=MetricsSeriesResponse)
async def metrics_series(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    agents: Optional[str] = None,  # comma-separated
):
    """Return daily series for calls and errors between dates, optionally filtered by agents."""
    try:
        if os_enabled():
            os_client = get_opensearch_client()
            must = []
            agent_list = [a for a in (agents.split(',') if agents else []) if a]
            if agent_list:
                must.append({"terms": {"agent_id": agent_list}})
            body = {
                "size": 0,
                "query": {"bool": {"must": must, "filter": [{"range": {"timestamp": {"gte": start_date or "now-30d/d", "lte": end_date or "now/d"}}}]}},
                "aggs": {
                    "by_day": {
                        "date_histogram": {
                            "field": "timestamp",
                            "calendar_interval": "day",
                            "min_doc_count": 0
                        },
                        "aggs": {
                            "errors": {"filter": {"term": {"message_type": "error"}}}
                        }
                    }
                }
            }
            res = os_client.search(index=Config.OPENSEARCH_INDEX_EVENTS, body=body)
            buckets = res.get('aggregations', {}).get('by_day', {}).get('buckets', [])
            points = [
                SeriesPoint(date=b.get('key_as_string', '')[:10], calls=b.get('doc_count', 0), errors=b.get('errors', {}).get('doc_count', 0), visitors=0)
                for b in buckets
            ]
            # Determine actual bounds from buckets if not provided
            if not start_date and buckets:
                start_date = buckets[0].get('key_as_string', '')[:10]
            if not end_date and buckets:
                end_date = buckets[-1].get('key_as_string', '')[:10]
            return MetricsSeriesResponse(start_date=start_date, end_date=end_date, agents=(agent_list or None), items=points)

        dynamodb = get_dynamodb_client()
        metrics_table = dynamodb.Table(Config.DYNAMODB_TABLE_METRICS)

        if not start_date or not end_date:
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=30)
            start_date = start_date or start_dt.strftime("%Y-%m-%d")
            end_date = end_date or end_dt.strftime("%Y-%m-%d")

        agent_list = [a for a in (agents.split(',') if agents else []) if a]

        # date -> totals
        from collections import defaultdict
        by_date_calls = defaultdict(int)
        by_date_errors = defaultdict(int)
        by_date_visitors = defaultdict(int)
        by_date_models = defaultdict(set)
        by_date_model_usage = defaultdict(dict)

        if agent_list:
            for aid in agent_list:
                resp = metrics_table.query(
                    KeyConditionExpression=boto3.dynamodb.conditions.Key('agent_id').eq(aid)
                    & boto3.dynamodb.conditions.Key('date').between(start_date, end_date)
                )
                for it in resp.get('Items', []):
                    d = it.get('date')
                    by_date_calls[d] += it.get('total_messages', 0)
                    by_date_errors[d] += it.get('total_errors', 0)
                    by_date_visitors[d] += it.get('unique_users', 0)
                    # Collect model information
                    models = it.get('models', [])
                    model_usage = it.get('model_usage', {})
                    if d not in by_date_models:
                        by_date_models[d] = set()
                        by_date_model_usage[d] = {}
                    by_date_models[d].update(models)
                    for model, count in model_usage.items():
                        by_date_model_usage[d][model] = by_date_model_usage[d].get(model, 0) + count
        else:
            from boto3.dynamodb.conditions import Attr
            resp = metrics_table.scan(
                FilterExpression=Attr('date').between(start_date, end_date)
            )
            for it in resp.get('Items', []):
                d = it.get('date')
                by_date_calls[d] += it.get('total_messages', 0)
                by_date_errors[d] += it.get('total_errors', 0)
                by_date_visitors[d] += it.get('unique_users', 0)
                # Collect model information
                models = it.get('models', [])
                model_usage = it.get('model_usage', {})
                if d not in by_date_models:
                    by_date_models[d] = set()
                    by_date_model_usage[d] = {}
                by_date_models[d].update(models)
                for model, count in model_usage.items():
                    by_date_model_usage[d][model] = by_date_model_usage[d].get(model, 0) + count

        # Build continuous range
        points: list[SeriesPoint] = []
        cur = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        while cur <= end:
            d = cur.strftime("%Y-%m-%d")
            points.append(SeriesPoint(
                date=d,
                calls=by_date_calls.get(d, 0),
                errors=by_date_errors.get(d, 0),
                visitors=by_date_visitors.get(d, 0),
                models=list(by_date_models.get(d, set())),
                model_usage=by_date_model_usage.get(d, {})
            ))
            cur += timedelta(days=1)

        return MetricsSeriesResponse(start_date=start_date, end_date=end_date, agents=(agent_list or None), items=points)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compute series: {str(e)}")


@router.get("/conversations", response_model=ConversationsResponse)
async def conversations(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    agent_id: Optional[str] = None,
    limit: int = 100,
):
    """Group events into conversations by metadata.conversation_id and summarize."""
    try:
        if os_enabled():
            os_client = get_opensearch_client()
            must = []
            if agent_id:
                must.append({"term": {"agent_id": agent_id}})
            body = {
                "size": 1000,
                "query": {"bool": {"must": must, "filter": [{"range": {"timestamp": {"gte": start_date or "now-7d/d", "lte": end_date or "now/d"}}}]}},
                "sort": [{"timestamp": {"order": "asc"}}]
            }
            res = os_client.search(index=Config.OPENSEARCH_INDEX_EVENTS, body=body)
            items = [h.get('_source', {}) for h in res.get('hits', {}).get('hits', [])]
            from collections import defaultdict
            grouped = defaultdict(list)
            for e in items:
                cid = e.get('conversation_id') or (e.get('metadata') or {}).get('conversation_id') or (e.get('metadata') or {}).get('trace_id')
                if not cid:
                    continue
                grouped[str(cid)].append(e)
            convs = []
            for cid, evs in grouped.items():
                evs_sorted = sorted(evs, key=lambda x: x.get('timestamp', ''))
                first = evs_sorted[0]
                last = evs_sorted[-1]
                start_ts = first.get('timestamp') or first.get('@timestamp')
                try:
                    start_dt = datetime.fromisoformat(start_ts.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat((last.get('timestamp') or start_ts).replace('Z', '+00:00'))
                    duration = int((end_dt - start_dt).total_seconds())
                except Exception:
                    duration = 0
                status = 'error' if any(e.get('message_type') == 'error' for e in evs_sorted) else 'completed'
                convs.append(ConversationItem(id=cid, agent_id=str(first.get('agent_id')), startedAt=start_ts, duration=duration, messageCount=len(evs_sorted), status=status))
            convs = sorted(convs, key=lambda c: c.startedAt, reverse=True)[:limit]
            return ConversationsResponse(items=convs)

        dynamodb = get_dynamodb_client()
        events_table = dynamodb.Table(Config.DYNAMODB_TABLE_EVENTS)

        if not start_date or not end_date:
            end_dt = datetime.now()
            start_dt = end_dt - timedelta(days=7)
            start_date = start_date or start_dt.strftime("%Y-%m-%d")
            end_date = end_date or end_dt.strftime("%Y-%m-%d")

        items = []
        if agent_id:
            resp = events_table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key('agent_id').eq(agent_id)
                & boto3.dynamodb.conditions.Key('timestamp').between(start_date, end_date + 'T23:59:59Z'),
                Limit=1000,
                ScanIndexForward=True,
            )
            items = resp.get('Items', [])
        else:
            from boto3.dynamodb.conditions import Attr
            resp = events_table.scan(
                FilterExpression=Attr('timestamp').between(start_date, end_date + 'T23:59:59Z'),
                Limit=1000,
            )
            items = resp.get('Items', [])

        # Group by conversation_id
        from collections import defaultdict
        grouped = defaultdict(list)
        for e in items:
            cid = None
            md = e.get('metadata')
            if isinstance(md, dict):
                cid = md.get('conversation_id') or md.get('trace_id')
            if not cid:
                # skip events without conversation/trace id
                continue
            grouped[cid].append(e)

        convs: list[ConversationItem] = []
        for cid, evs in grouped.items():
            evs_sorted = sorted(evs, key=lambda x: x.get('timestamp', ''))
            first = evs_sorted[0]
            last = evs_sorted[-1]
            start_ts = first.get('timestamp')
            # duration in seconds if both parse OK
            try:
                start_dt = datetime.fromisoformat(start_ts.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(last.get('timestamp', start_ts).replace('Z', '+00:00'))
                duration = int((end_dt - start_dt).total_seconds())
            except Exception:
                duration = 0
            msg_count = len(evs_sorted)
            status = 'error' if any(e.get('message_type') == 'error' for e in evs_sorted) else 'completed'
            convs.append(ConversationItem(
                id=str(cid),
                agent_id=str(first.get('agent_id')),
                startedAt=start_ts,
                duration=duration,
                messageCount=msg_count,
                status=status,
            ))

        # limit results
        convs = sorted(convs, key=lambda c: c.startedAt, reverse=True)[:limit]
        return ConversationsResponse(items=convs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list conversations: {str(e)}")


@router.post("/traces/spans")
async def ingest_spans(payload: dict):
    """Ingest OpenTelemetry-style spans. Accepts a JSON body with 'spans': [ ... ]."""
    try:
        spans = payload.get('spans', [])
        if not isinstance(spans, list) or not spans:
            raise HTTPException(status_code=400, detail="Body must include non-empty 'spans' array")
        indexed = 0
        os_client = None
        if os_enabled():
            os_client = get_opensearch_client()
        for sp in spans:
            # Normalize fields
            doc = {
                'trace_id': sp.get('trace_id'),
                'span_id': sp.get('span_id'),
                'parent_span_id': sp.get('parent_span_id'),
                'name': sp.get('name'),
                'start_time': sp.get('start_time'),
                'end_time': sp.get('end_time'),
                'status': sp.get('status'),
                'service_name': sp.get('service_name') or (sp.get('resource') or {}).get('service.name'),
                'attributes': sp.get('attributes'),
                '@timestamp': sp.get('start_time'),
            }
            if os_client:
                os_client.index(index=Config.OPENSEARCH_INDEX_SPANS, document=doc)
                indexed += 1
        return {"ingested": indexed}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ingest spans: {str(e)}")


@router.get("/traces/{trace_id}")
async def get_trace(trace_id: str):
    """Return spans for a given trace_id and a basic summary. Uses OpenSearch when enabled."""
    try:
        spans_out = []
        if os_enabled():
            os_client = get_opensearch_client()
            res = os_client.search(index=Config.OPENSEARCH_INDEX_SPANS, body={
                "size": 1000,
                "query": {"term": {"trace_id": trace_id}},
                "sort": [{"start_time": {"order": "asc"}}]
            })
            for h in res.get('hits', {}).get('hits', []):
                s = h.get('_source', {})
                spans_out.append({
                    'trace_id': s.get('trace_id'),
                    'span_id': s.get('span_id'),
                    'parent_span_id': s.get('parent_span_id'),
                    'name': s.get('name'),
                    'start_time': s.get('start_time'),
                    'end_time': s.get('end_time'),
                    'status': s.get('status'),
                    'service_name': s.get('service_name'),
                    'attributes': s.get('attributes'),
                })
        # Compute summary
        start_ts = spans_out[0]['start_time'] if spans_out else None
        end_ts = spans_out[-1]['end_time'] if spans_out and spans_out[-1].get('end_time') else (spans_out[-1]['start_time'] if spans_out else None)
        duration_ms = None
        try:
            if start_ts and end_ts:
                sdt = datetime.fromisoformat(start_ts.replace('Z', '+00:00'))
                edt = datetime.fromisoformat(end_ts.replace('Z', '+00:00'))
                duration_ms = int((edt - sdt).total_seconds() * 1000)
        except Exception:
            duration_ms = None
        return {
            'trace_id': trace_id,
            'start_time': start_ts,
            'end_time': end_ts,
            'duration_ms': duration_ms,
            'spans': spans_out,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trace: {str(e)}")

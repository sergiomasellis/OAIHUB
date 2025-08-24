#!/usr/bin/env bash
set -euo pipefail

OS_URL=${OS_URL:-http://localhost:9200}
EVENTS_INDEX=${EVENTS_INDEX:-events-v1}
SPANS_INDEX=${SPANS_INDEX:-spans-v1}

echo "Creating index: $EVENTS_INDEX"
curl -sS -X PUT "$OS_URL/$EVENTS_INDEX" \
  -H 'Content-Type: application/json' \
  --data-binary @"$(dirname "$0")/events-index.json" | jq .acknowledged || true

echo "Creating index: $SPANS_INDEX"
curl -sS -X PUT "$OS_URL/$SPANS_INDEX" \
  -H 'Content-Type: application/json' \
  --data-binary @"$(dirname "$0")/spans-index.json" | jq .acknowledged || true

echo "Indexing demo events"
now=$(date -u +%Y-%m-%dT%H:%M:%SZ)
day=$(date -u +%Y-%m-%d)
curl -sS -X POST "$OS_URL/$EVENTS_INDEX/_bulk" -H 'Content-Type: application/x-ndjson' --data-binary @- <<EOF | jq .errors
{"index":{}}
{"@timestamp":"$now","timestamp":"$now","agent_id":"agent-1","message_type":"user_message","content":"Hello","token_count":12,"model_used":"gpt-4o","trace_id":"trace-demo-1","conversation_id":"conv-demo-1"}
{"index":{}}
{"@timestamp":"$now","timestamp":"$now","agent_id":"agent-1","message_type":"agent_response","content":"Hi! How can I help?","token_count":64,"response_time_ms":240,"model_used":"gpt-4o","trace_id":"trace-demo-1","conversation_id":"conv-demo-1"}
{"index":{}}
{"@timestamp":"$now","timestamp":"$now","agent_id":"agent-2","message_type":"error","error_details":"Rate limit","model_used":"gpt-3.5","trace_id":"trace-demo-2","conversation_id":"conv-demo-2"}
EOF

echo "Indexing demo spans"
curl -sS -X POST "$OS_URL/$SPANS_INDEX/_bulk" -H 'Content-Type: application/x-ndjson' --data-binary @- <<EOF | jq .errors
{"index":{}}
{"trace_id":"trace-demo-1","span_id":"span-1","name":"conversation","start_time":"$now","end_time":"$now","status":"OK","service_name":"agent-service","@timestamp":"$now"}
{"index":{}}
{"trace_id":"trace-demo-1","span_id":"span-2","parent_span_id":"span-1","name":"llm.call","start_time":"$now","end_time":"$now","status":"OK","service_name":"agent-service","@timestamp":"$now"}
EOF

echo "Done. Open http://localhost:5601 to explore."


# Local Development Scripts

This directory contains scripts to help with local development setup and data population.

## 🚀 Quick Start

After running `docker-compose up -d`, populate sample data:

```bash
# Make script executable (first time only)
chmod +x scripts/setup-local-data.sh

# Run the setup script
./scripts/setup-local-data.sh
```

## 📊 What Gets Populated

The setup script creates:
- ✅ **DynamoDB tables** for events and metrics
- ✅ **Sample metrics data** (July-Aug 2025)
- ✅ **Sample events data** for agents
- ✅ **Realistic KPI values** and time series data

## 📈 Sample Data Overview

**Date Range**: July 25 - August 24, 2025

**Agents**: agent-1, agent-2

**Metrics**:
- **KPI Totals**: 850+ calls, 1.2% error rate, 223ms latency
- **Time Series**: Daily visitors, calls, and errors
- **Agent Filtering**: Compare usage between agents

## 🔄 Resetting Data

To reset the sample data:

```bash
# Stop containers and remove volumes
docker-compose down -v

# Restart services
docker-compose up -d

# Repopulate sample data
./scripts/setup-local-data.sh
```

## 📁 Files

- `setup-local-data.sh` - Main setup script (recommended)
- `populate_sample_data.py` - Python alternative (requires boto3)
- `README.md` - This documentation

## 🌐 Access Your Dashboard

After setup, visit:
- **Dashboard**: http://localhost:3000
- **API Health**: http://localhost:8001/health
- **KPI Endpoint**: http://localhost:8001/api/v1/dashboard/kpis
- **Metrics Series**: http://localhost:8001/api/v1/metrics/series
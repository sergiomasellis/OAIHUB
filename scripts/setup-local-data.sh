#!/bin/bash

# Setup Local Development Data
# This script populates sample data for local development after docker-compose up

set -e

echo "🚀 Setting up local development data..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Wait for services to be ready
wait_for_service() {
    local service_name=$1
    local url=$2
    local max_attempts=30

    print_status "Waiting for $service_name to be ready at $url..."

    for ((i=1; i<=max_attempts; i++)); do
        if curl -s "$url" > /dev/null 2>&1; then
            print_success "$service_name is ready!"
            return 0
        fi

        echo -n "."
        sleep 1
    done

    print_error "$service_name not ready after $max_attempts seconds"
    return 1
}

# Main setup process
main() {
    print_status "Starting local development data setup..."

    # Wait for DynamoDB Local
    if ! wait_for_service "DynamoDB Local" "http://localhost:8000"; then
        print_error "DynamoDB Local is not available. Make sure docker-compose is running."
        exit 1
    fi

    # Wait for Backend API
    if ! wait_for_service "Backend API" "http://localhost:8001/health"; then
        print_error "Backend API is not available. Make sure docker-compose is running."
        exit 1
    fi

    # Copy the setup script to the backend container
    print_status "Copying setup script to backend container..."
    docker cp infrastructure/setup_dynamodb.py oaihub-backend-1:/app/setup_dynamodb.py

    # Run the setup script in the container
    print_status "Running DynamoDB setup script..."
    docker-compose exec -T backend python /app/setup_dynamodb.py

    print_success "✅ Local development data setup complete!"
    print_status ""
    print_status "Your dashboard should now show sample data:"
    print_status "  📊 KPI Metrics: http://localhost:3000"
    print_status "  📈 Time Series: Agent usage over time"
    print_status "  👥 Agents: agent-1, agent-2"
    print_status ""
    print_status "To reset data, run: docker-compose down && docker-compose up -d"
    print_status "Then re-run this script: ./scripts/setup-local-data.sh"
}

# Run main function
main "$@"
#!/bin/bash

# CR7 Token Bot - Production Deployment Script
# This script handles the complete deployment process

set -e  # Exit on any error

echo "🚀 CR7 Token Bot - Production Deployment"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_error ".env file not found!"
    print_warning "Please copy env_template.txt to .env and fill in your values"
    print_warning "Or copy production.env to .env for production settings"
    exit 1
fi

# Check if required environment variables are set
print_status "Checking environment variables..."

required_vars=("TELEGRAM_BOT_TOKEN" "TELEGRAM_GROUP_ID" "TOKEN_MINT")
missing_vars=()

for var in "${required_vars[@]}"; do
    if ! grep -q "^${var}=" .env || grep -q "^${var}=$" .env || grep -q "^${var}=your_" .env; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    print_error "Missing or incomplete environment variables:"
    for var in "${missing_vars[@]}"; do
        echo "  - $var"
    done
    print_warning "Please update your .env file with the correct values"
    exit 1
fi

print_status "Environment variables check passed!"

# Create logs directory
print_status "Creating logs directory..."
mkdir -p logs

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed!"
    print_warning "Please install Docker to continue with containerized deployment"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed!"
    print_warning "Please install Docker Compose to continue"
    exit 1
fi

print_status "Docker and Docker Compose are available!"

# Build and start the application
print_status "Building Docker image..."
docker-compose build

print_status "Starting CR7 Token Bot..."
docker-compose up -d

# Wait for the service to be healthy
print_status "Waiting for service to be healthy..."
sleep 10

# Check if the service is running
if docker-compose ps | grep -q "Up"; then
    print_status "✅ CR7 Token Bot is running successfully!"
    print_status "Health check endpoint: http://localhost:8000/health"
    print_status "Metrics endpoint: http://localhost:8000/metrics"
    print_status "View logs with: docker-compose logs -f"
else
    print_error "❌ Failed to start CR7 Token Bot"
    print_warning "Check logs with: docker-compose logs"
    exit 1
fi

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Useful commands:"
echo "  View logs:     docker-compose logs -f"
echo "  Stop bot:      docker-compose down"
echo "  Restart bot:   docker-compose restart"
echo "  Update bot:    docker-compose pull && docker-compose up -d"
echo ""
echo "🔍 Monitoring:"
echo "  Health check:  curl http://localhost:8000/health"
echo "  Metrics:       curl http://localhost:8000/metrics"
echo ""

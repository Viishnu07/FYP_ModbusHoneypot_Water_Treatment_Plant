#!/bin/bash
# Startup script for Modbus Water Treatment Plant Simulator

echo "=========================================="
echo "  Modbus Water Treatment Plant Simulator"
echo "=========================================="
echo ""

# Create log directories
echo "Creating log directories..."
mkdir -p logs/modbus logs/hmi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "Error: docker-compose is not installed."
    exit 1
fi

# Start services
echo "Starting services..."
docker-compose up -d

# Wait a moment for services to initialize
echo "Waiting for services to start..."
sleep 3

# Check service status
echo ""
echo "Service status:"
docker-compose ps

echo ""
echo "=========================================="
echo "✓ Services started successfully!"
echo "=========================================="
echo ""
echo "Access points:"
echo "  • HMI Dashboard:    http://localhost:5000"
echo "  • Modbus TCP:       localhost:502"
echo ""
echo "Commands:"
echo "  • View logs:        docker-compose logs -f"
echo "  • Stop services:    docker-compose down"
echo "  • Restart services: docker-compose restart"
echo ""
echo "Log files:"
echo "  • Modbus logs:      logs/modbus/modbus_operations.json"
echo "  • HMI logs:         logs/hmi/hmi_access.json"
echo ""

# PowerShell startup script for Modbus Water Treatment Plant Simulator

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Modbus Water Treatment Plant Simulator" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Create log directories
Write-Host "Creating log directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "logs\modbus" | Out-Null
New-Item -ItemType Directory -Force -Path "logs\hmi" | Out-Null

# Check if Docker is running
Write-Host "Checking Docker status..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Error: Docker is not installed or not running." -ForegroundColor Red
    exit 1
}

# Check if docker-compose is available
Write-Host "Checking docker-compose..." -ForegroundColor Yellow
try {
    docker-compose --version | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: docker-compose is not available." -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Error: docker-compose is not installed." -ForegroundColor Red
    exit 1
}

# Start services
Write-Host "Starting services..." -ForegroundColor Yellow
docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to start services." -ForegroundColor Red
    exit 1
}

# Wait for services to initialize
Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Check service status
Write-Host ""
Write-Host "Service status:" -ForegroundColor Yellow
docker-compose ps

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "[OK] Services started successfully!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access points:" -ForegroundColor Cyan
Write-Host "  - HMI Dashboard:    http://localhost:5000" -ForegroundColor White
Write-Host "  - Modbus TCP:       localhost:502" -ForegroundColor White
Write-Host ""
Write-Host "Commands:" -ForegroundColor Cyan
Write-Host "  - View logs:        docker-compose logs -f" -ForegroundColor White
Write-Host "  - Stop services:    docker-compose down" -ForegroundColor White
Write-Host "  - Restart services: docker-compose restart" -ForegroundColor White
Write-Host ""
Write-Host "Log files:" -ForegroundColor Cyan
Write-Host "  - Modbus logs:      logs\modbus\modbus_operations.json" -ForegroundColor White
Write-Host "  - HMI logs:         logs\hmi\hmi_access.json" -ForegroundColor White
Write-Host ""

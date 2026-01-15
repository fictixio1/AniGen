# AniGen Setup Script for Windows
# Automates installation and configuration

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  AniGen - Infinite Anime Director Setup  " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "[1/5] Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python not found. Please install Python 3.11+ from https://www.python.org/" -ForegroundColor Red
    exit 1
}

# Check PostgreSQL
Write-Host "[2/5] Checking PostgreSQL..." -ForegroundColor Yellow
$pgCheck = Get-Command psql -ErrorAction SilentlyContinue
$dockerCheck = Get-Command docker -ErrorAction SilentlyContinue

if ($pgCheck) {
    Write-Host "✓ PostgreSQL found (local installation)" -ForegroundColor Green
    $useDocker = $false
} elseif ($dockerCheck) {
    Write-Host "✓ Docker found (will use containerized PostgreSQL)" -ForegroundColor Green
    $useDocker = $true
} else {
    Write-Host "✗ Neither PostgreSQL nor Docker found." -ForegroundColor Red
    Write-Host "  Install one of:" -ForegroundColor Yellow
    Write-Host "    - PostgreSQL: https://www.postgresql.org/download/" -ForegroundColor Yellow
    Write-Host "    - Docker Desktop: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Install Python dependencies
Write-Host "[3/5] Installing Python dependencies..." -ForegroundColor Yellow
python -m pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Setup database
Write-Host "[4/5] Setting up database..." -ForegroundColor Yellow
if ($useDocker) {
    Write-Host "  Starting PostgreSQL container..." -ForegroundColor Cyan
    docker compose up -d postgres
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ PostgreSQL container started" -ForegroundColor Green
        Write-Host "  Waiting for database to be ready..." -ForegroundColor Cyan
        Start-Sleep -Seconds 5
    } else {
        Write-Host "✗ Failed to start PostgreSQL container" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  Checking database connection..." -ForegroundColor Cyan
    $env:PGPASSWORD = "anigen_password"
    $dbExists = psql -U anigen_user -d anigen -h localhost -c "SELECT 1" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  Database not found. Creating..." -ForegroundColor Cyan
        Write-Host "  Please enter PostgreSQL admin password when prompted:" -ForegroundColor Yellow
        psql -U postgres -h localhost -c "CREATE DATABASE anigen;"
        psql -U postgres -h localhost -c "CREATE USER anigen_user WITH PASSWORD 'anigen_password';"
        psql -U postgres -h localhost -c "GRANT ALL PRIVILEGES ON DATABASE anigen TO anigen_user;"
    }

    Write-Host "  Initializing schema..." -ForegroundColor Cyan
    psql -U anigen_user -d anigen -h localhost -f schemas/database_schema.sql
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Database ready" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to initialize database" -ForegroundColor Red
        exit 1
    }
}

# Verify .env file
Write-Host "[5/5] Checking configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✓ Configuration file found" -ForegroundColor Green
} else {
    Write-Host "  Creating .env from template..." -ForegroundColor Cyan
    Copy-Item ".env.example" ".env"
    Write-Host "✓ Configuration file created" -ForegroundColor Green
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Setup Complete! " -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "To start the system in mock mode:" -ForegroundColor Cyan
Write-Host "  python main.py" -ForegroundColor White
Write-Host ""
Write-Host "To stop: Press Ctrl+C" -ForegroundColor Cyan
Write-Host ""
Write-Host "To check database:" -ForegroundColor Cyan
if ($useDocker) {
    Write-Host "  docker exec -it anigen_postgres psql -U anigen_user -d anigen" -ForegroundColor White
} else {
    Write-Host "  psql -U anigen_user -d anigen -h localhost" -ForegroundColor White
}
Write-Host ""
Write-Host "For more information, see README.md and SETUP.md" -ForegroundColor Yellow
Write-Host ""

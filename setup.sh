#!/bin/bash
# AniGen Setup Script for Linux/Mac

set -e

echo "============================================"
echo "  AniGen - Infinite Anime Director Setup  "
echo "============================================"
echo ""

# Check Python
echo "[1/5] Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ Python found: $PYTHON_VERSION"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo "✓ Python found: $PYTHON_VERSION"
    PYTHON_CMD="python"
else
    echo "✗ Python not found. Please install Python 3.11+"
    exit 1
fi

# Check PostgreSQL or Docker
echo "[2/5] Checking PostgreSQL..."
USE_DOCKER=false
if command -v psql &> /dev/null; then
    echo "✓ PostgreSQL found (local installation)"
    USE_DOCKER=false
elif command -v docker &> /dev/null; then
    echo "✓ Docker found (will use containerized PostgreSQL)"
    USE_DOCKER=true
else
    echo "✗ Neither PostgreSQL nor Docker found."
    echo "  Install one of:"
    echo "    - PostgreSQL: https://www.postgresql.org/download/"
    echo "    - Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Install Python dependencies
echo "[3/5] Installing Python dependencies..."
$PYTHON_CMD -m pip install -r requirements.txt --quiet
echo "✓ Dependencies installed"

# Setup database
echo "[4/5] Setting up database..."
if [ "$USE_DOCKER" = true ]; then
    echo "  Starting PostgreSQL container..."
    docker compose up -d postgres
    echo "✓ PostgreSQL container started"
    echo "  Waiting for database to be ready..."
    sleep 5
else
    echo "  Checking database connection..."
    export PGPASSWORD="anigen_password"
    if ! psql -U anigen_user -d anigen -h localhost -c "SELECT 1" &> /dev/null; then
        echo "  Database not found. Creating..."
        echo "  Please enter PostgreSQL admin password when prompted:"
        psql -U postgres -h localhost -c "CREATE DATABASE anigen;"
        psql -U postgres -h localhost -c "CREATE USER anigen_user WITH PASSWORD 'anigen_password';"
        psql -U postgres -h localhost -c "GRANT ALL PRIVILEGES ON DATABASE anigen TO anigen_user;"
    fi

    echo "  Initializing schema..."
    psql -U anigen_user -d anigen -h localhost -f schemas/database_schema.sql
    echo "✓ Database ready"
fi

# Verify .env file
echo "[5/5] Checking configuration..."
if [ -f ".env" ]; then
    echo "✓ Configuration file found"
else
    echo "  Creating .env from template..."
    cp .env.example .env
    echo "✓ Configuration file created"
fi

echo ""
echo "============================================"
echo "  Setup Complete! "
echo "============================================"
echo ""
echo "To start the system in mock mode:"
echo "  $PYTHON_CMD main.py"
echo ""
echo "To stop: Press Ctrl+C"
echo ""
echo "To check database:"
if [ "$USE_DOCKER" = true ]; then
    echo "  docker exec -it anigen_postgres psql -U anigen_user -d anigen"
else
    echo "  psql -U anigen_user -d anigen -h localhost"
fi
echo ""
echo "For more information, see README.md and SETUP.md"
echo ""

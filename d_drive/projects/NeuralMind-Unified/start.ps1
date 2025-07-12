# FusionAI Companion - PowerShell Startup Script

Write-Host "FusionAI Companion - PowerShell Startup Script" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""

# Function to check if command exists
function Test-CommandExists {
    param($command)
    try {
        Get-Command $command -ErrorAction Stop
        return $true
    }
    catch {
        return $false
    }
}

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Check Python
if (-not (Test-CommandExists "python")) {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ and try again" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Docker
if (-not (Test-CommandExists "docker")) {
    Write-Host "Error: Docker is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Docker Desktop and try again" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if we're in the right directory
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "Error: Please run this script from the FusionAI-Companion root directory" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Prerequisites check passed!" -ForegroundColor Green
Write-Host ""

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Install/upgrade dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host ""
    Write-Host "IMPORTANT: Please edit .env file with your API keys before continuing" -ForegroundColor Red
    $response = Read-Host "Would you like to open .env file now? (y/n)"
    if ($response -eq "y" -or $response -eq "Y") {
        notepad .env
    }
}

# Start Docker services
Write-Host "Starting Docker services..." -ForegroundColor Yellow
docker-compose up -d

# Wait for services to start
Write-Host "Waiting for services to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check service health
Write-Host "Checking service health..." -ForegroundColor Yellow
$services = @(
    @{ Name = "Ollama"; Port = 11434 },
    @{ Name = "Supabase DB"; Port = 5432 },
    @{ Name = "Neo4j"; Port = 7474 },
    @{ Name = "n8n"; Port = 5678 },
    @{ Name = "Open WebUI"; Port = 3000 }
)

foreach ($service in $services) {
    try {
        $connection = Test-NetConnection -ComputerName "localhost" -Port $service.Port -WarningAction SilentlyContinue
        if ($connection.TcpTestSucceeded) {
            Write-Host "✓ $($service.Name) is running on port $($service.Port)" -ForegroundColor Green
        }
        else {
            Write-Host "⚠ $($service.Name) is not responding on port $($service.Port)" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "⚠ Could not check $($service.Name) on port $($service.Port)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Starting FusionAI Companion..." -ForegroundColor Green
Write-Host ""

# Start the main application
try {
    python main.py
}
catch {
    Write-Host "Error starting FusionAI Companion: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "FusionAI Companion has stopped." -ForegroundColor Yellow
Read-Host "Press Enter to exit"

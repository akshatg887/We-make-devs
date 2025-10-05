# CSV Agent Quick Start Script
# Run this script to start the CSV agent backend

Write-Host "🚀 Starting CSV Agent Backend..." -ForegroundColor Cyan
Write-Host ""

# Check if we're in the csv-agent directory
if (-not (Test-Path "app_analyze.py")) {
    Write-Host "❌ Error: Please run this script from the csv-agent directory" -ForegroundColor Red
    Write-Host "   cd csv-agent" -ForegroundColor Yellow
    Write-Host "   .\start_csv_agent.ps1" -ForegroundColor Yellow
    exit 1
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  Warning: .env file not found!" -ForegroundColor Yellow
    Write-Host "   Creating a template .env file..." -ForegroundColor Yellow
    @"
CEREBRAS_API_KEY=your_cerebras_api_key_here
CEREBRAS_MODEL=qwen-3-235b-a22b-instruct-2507
"@ | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "   ✅ Created .env template. Please edit it and add your CEREBRAS_API_KEY" -ForegroundColor Green
    Write-Host ""
    notepad .env
    Read-Host "Press Enter after you've saved your API key in .env"
}

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "   ✅ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Check if requirements are installed
Write-Host "📚 Checking dependencies..." -ForegroundColor Yellow
$pipList = pip list
if (-not ($pipList -match "fastapi")) {
    Write-Host "   Installing dependencies from requirements.txt..." -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
    Write-Host "   ✅ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "   ✅ Dependencies already installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "   CSV AGENT BACKEND" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 Starting server on http://localhost:8001" -ForegroundColor Green
Write-Host "📚 API Docs: http://localhost:8001/docs" -ForegroundColor Green
Write-Host "❤️  Health Check: http://localhost:8001/health" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# Start the server
uvicorn app_analyze:app --reload --port 8001

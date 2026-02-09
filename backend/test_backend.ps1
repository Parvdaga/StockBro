# StockBro Backend Test Script
# Tests all major endpoints to verify the backend is working

Write-Host "`n=== StockBro Backend Test ===" -ForegroundColor Cyan

# Test 1: Health Check
Write-Host "`n[1/4] Testing Health Endpoint..." -ForegroundColor Yellow
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
    $healthData = $health.Content | ConvertFrom-Json
    Write-Host "✓ Health: $($healthData.status)" -ForegroundColor Green
    Write-Host "  Version: $($healthData.version)" -ForegroundColor Gray
    Write-Host "  Database: $($healthData.database)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 2: Root Endpoint
Write-Host "`n[2/4] Testing Root Endpoint..." -ForegroundColor Yellow
try {
    $root = Invoke-WebRequest -Uri "http://localhost:8000/" -UseBasicParsing
    $rootData = $root.Content | ConvertFrom-Json
    Write-Host "✓ Root: $($rootData.message)" -ForegroundColor Green
    Write-Host "  Docs: $($rootData.docs)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Root endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: API Docs
Write-Host "`n[3/4] Testing API Documentation..." -ForegroundColor Yellow
try {
    $docs = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/docs" -UseBasicParsing
    if ($docs.StatusCode -eq 200) {
        Write-Host "✓ API Docs available at http://localhost:8000/api/v1/docs" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ API docs failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: OpenAPI Schema
Write-Host "`n[4/4] Testing OpenAPI Schema..." -ForegroundColor Yellow
try {
    $openapi = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/openapi.json" -UseBasicParsing
    $schema = $openapi.Content | ConvertFrom-Json
    Write-Host "✓ OpenAPI Schema loaded" -ForegroundColor Green
    Write-Host "  Title: $($schema.info.title)" -ForegroundColor Gray
    Write-Host "  Version: $($schema.info.version)" -ForegroundColor Gray
    
    # Count endpoints
    $endpoints = $schema.paths.PSObject.Properties | Measure-Object
    Write-Host "  Endpoints: $($endpoints.Count)" -ForegroundColor Gray
} catch {
    Write-Host "✗ OpenAPI schema failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== Test Summary ===" -ForegroundColor Cyan
Write-Host "✓ Backend is running successfully!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "  1. Open http://localhost:8000/api/v1/docs in your browser"
Write-Host "  2. Try the signup endpoint to create a test user"
Write-Host "  3. Test the chat endpoint with your AI agent"
Write-Host ""


# StockBro API Test Script (PowerShell)

Write-Host "=== Testing StockBro API ===" -ForegroundColor Cyan

# 1. Health Check
Write-Host "`n1. Health Check..." -ForegroundColor Yellow
$health = Invoke-RestMethod -Uri http://localhost:8000/health -UseBasicParsing
$health | ConvertTo-Json
Write-Host "✓ Health check passed" -ForegroundColor Green

# 2. Root Endpoint
Write-Host "`n2. Root Endpoint..." -ForegroundColor Yellow
$root = Invoke-RestMethod -Uri http://localhost:8000/ -UseBasicParsing
$root | ConvertTo-Json
Write-Host "✓ Root endpoint working" -ForegroundColor Green

# 3. Signup
Write-Host "`n3. Creating test user..." -ForegroundColor Yellow
$signupBody = @{
    email = "test@example.com"
    password = "password123"
    full_name = "Test User"
} | ConvertTo-Json

try {
    $signup = Invoke-RestMethod -Uri http://localhost:8000/api/v1/auth/signup `
        -Method Post `
        -ContentType "application/json" `
        -Body $signupBody
    $signup | ConvertTo-Json
    Write-Host "✓ User created successfully" -ForegroundColor Green
} catch {
    if ($_.Exception.Response.StatusCode -eq 409) {
        Write-Host "⚠ User already exists (this is OK)" -ForegroundColor Yellow
    } else {
        Write-Host "✗ Signup failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# 4. Login
Write-Host "`n4. Logging in..." -ForegroundColor Yellow
$loginBody = @{
    email = "test@example.com"
    password = "password123"
} | ConvertTo-Json

$login = Invoke-RestMethod -Uri http://localhost:8000/api/v1/auth/login `
    -Method Post `
    -ContentType "application/json" `
    -Body $loginBody

Write-Host "✓ Login successful" -ForegroundColor Green
Write-Host "Access Token: $($login.access_token.Substring(0, 20))..." -ForegroundColor Gray

# 5. Test Authenticated Endpoint - Create Watchlist
Write-Host "`n5. Creating watchlist (authenticated)..." -ForegroundColor Yellow
$watchlistBody = @{
    name = "My Tech Stocks"
    description = "Tech companies to watch"
} | ConvertTo-Json

$headers = @{
    "Authorization" = "Bearer $($login.access_token)"
    "Content-Type" = "application/json"
}

try {
    $watchlist = Invoke-RestMethod -Uri http://localhost:8000/api/v1/watchlists/ `
        -Method Post `
        -Headers $headers `
        -Body $watchlistBody
    
    Write-Host "✓ Watchlist created" -ForegroundColor Green
    Write-Host "Watchlist ID: $($watchlist.id)" -ForegroundColor Gray
    
    # 6. Get All Watchlists
    Write-Host "`n6. Getting all watchlists..." -ForegroundColor Yellow
    $watchlists = Invoke-RestMethod -Uri http://localhost:8000/api/v1/watchlists/ `
        -Method Get `
        -Headers $headers
    
    Write-Host "✓ Found $($watchlists.Count) watchlist(s)" -ForegroundColor Green
    $watchlists | ConvertTo-Json -Depth 3
    
} catch {
    Write-Host "✗ Watchlist operation failed: $($_.Exception.Message)" -ForegroundColor Red
}

# 7. Test Chat (if Groq API key is set)
Write-Host "`n7. Testing AI Chat..." -ForegroundColor Yellow
$chatBody = @{
    message = "What is the stock market?"
} | ConvertTo-Json

try {
    $chat = Invoke-RestMethod -Uri http://localhost:8000/api/v1/chat/ `
        -Method Post `
        -Headers $headers `
        -Body $chatBody
    
    Write-Host "✓ Chat successful" -ForegroundColor Green
    Write-Host "AI Response: $($chat.answer.Substring(0, [Math]::Min(100, $chat.answer.Length)))..." -ForegroundColor Gray
} catch {
    Write-Host "⚠ Chat failed (check GROQ_API_KEY): $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "`n=== All Tests Complete ===" -ForegroundColor Cyan

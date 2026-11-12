$baseUrl = "http://127.0.0.1:8001"

Write-Host "`n========================================================" -ForegroundColor Cyan
Write-Host "AMK IDENTITY SERVICE - END-TO-END TEST SUITE" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

# Test 1: Health Check
Write-Host "`n[TEST 1] Checking Health Endpoint..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get
    Write-Host "PASSED: Service is healthy! ($($health.service))" -ForegroundColor Green
} catch {
    Write-Host "FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Fetch Dynamic Roles
Write-Host "`n[TEST 2] Fetching Active Roles from Supabase..." -ForegroundColor Yellow
try {
    $roles = Invoke-RestMethod -Uri "$baseUrl/api/v1/roles" -Method Get
    Write-Host "PASSED: Retrieved $($roles.Count) roles from Supabase database:" -ForegroundColor Green
    foreach ($r in $roles) {
        Write-Host "  - $($r.role_id) (Level: $($r.hierarchy_level), Self-Register: $($r.is_self_registerable))" -ForegroundColor Gray
    }
} catch {
    Write-Host "FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Login as Pre-seeded Student
Write-Host "`n[TEST 3] Testing Login with Pre-seeded Student (22731A0501)..." -ForegroundColor Yellow
$loginBody = @{
    login_identifier = "22731A0501"
    password = "Password123!"
} | ConvertTo-Json

try {
    $loginResp = Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
    Write-Host "PASSED: Student Login Successful!" -ForegroundColor Green
    Write-Host "  User ID: $($loginResp.user.user_id)" -ForegroundColor Green
    Write-Host "  Full Name: $($loginResp.user.full_name)" -ForegroundColor Green
    Write-Host "  Role: $($loginResp.user.role_id)" -ForegroundColor Green
    Write-Host "  Token Type: $($loginResp.token_type) (Token length: $($loginResp.access_token.Length))" -ForegroundColor Green
} catch {
    Write-Host "FAILED: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails) { Write-Host "Details: $($_.ErrorDetails.Message)" -ForegroundColor Red }
}

# Test 4: Register a Brand New Student
$randomNum = Get-Random -Minimum 1000 -Maximum 9999
$newRollNumber = "22731A$randomNum"
$newEmail = "student$randomNum@srit.ac.in"
$newPassword = "TestPassword@2026"

Write-Host "`n[TEST 4] Registering a Brand New Student ($newRollNumber)..." -ForegroundColor Yellow
$registerBody = @{
    tenant_id = "SRIT-ATP"
    roll_number = $newRollNumber
    email = $newEmail
    password = $newPassword
    full_name = "Automated Test Student $randomNum"
    department = "CSE"
    batch_year = "2022-2026"
} | ConvertTo-Json

try {
    $regResp = Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/register/student" -Method Post -Body $registerBody -ContentType "application/json"
    Write-Host "PASSED: Student Registered Successfully!" -ForegroundColor Green
    Write-Host "  User ID (Roll Number): $($regResp.user_id)" -ForegroundColor Green
    Write-Host "  Tenant ID: $($regResp.tenant_id)" -ForegroundColor Green
    Write-Host "  Role ID: $($regResp.role_id)" -ForegroundColor Green
} catch {
    Write-Host "FAILED: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails) { Write-Host "Details: $($_.ErrorDetails.Message)" -ForegroundColor Red }
}

# Test 5: Login with the Newly Registered Student
Write-Host "`n[TEST 5] Logging in with Newly Registered Student ($newRollNumber)..." -ForegroundColor Yellow
$newLoginBody = @{
    login_identifier = $newRollNumber
    password = $newPassword
} | ConvertTo-Json

try {
    $newLoginResp = Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/login" -Method Post -Body $newLoginBody -ContentType "application/json"
    Write-Host "PASSED: Login with Newly Registered Student Successful!" -ForegroundColor Green
    Write-Host "  Logged in as: $($newLoginResp.user.full_name) ($($newLoginResp.user.user_id))" -ForegroundColor Green
    Write-Host "  JWT Token issued successfully!" -ForegroundColor Green
} catch {
    Write-Host "FAILED: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails) { Write-Host "Details: $($_.ErrorDetails.Message)" -ForegroundColor Red }
}

# Test 6: Login with Email instead of Roll Number
Write-Host "`n[TEST 6] Testing Login using Email instead of Roll Number ($newEmail)..." -ForegroundColor Yellow
$emailLoginBody = @{
    login_identifier = $newEmail
    password = $newPassword
} | ConvertTo-Json

try {
    $emailLoginResp = Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/login" -Method Post -Body $emailLoginBody -ContentType "application/json"
    Write-Host "PASSED: Unified Login via Email Successful!" -ForegroundColor Green
    Write-Host "  Resolved User ID: $($emailLoginResp.user.user_id)" -ForegroundColor Green
} catch {
    Write-Host "FAILED: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails) { Write-Host "Details: $($_.ErrorDetails.Message)" -ForegroundColor Red }
}

# Test 7: Login as Admin and Provision a Staff Member
Write-Host "`n[TEST 7] Testing Admin Login & Staff Provisioning..." -ForegroundColor Yellow
$adminLoginBody = @{
    login_identifier = "ADM-SRIT-001"
    password = "Password123!"
} | ConvertTo-Json

try {
    $adminLoginResp = Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/login" -Method Post -Body $adminLoginBody -ContentType "application/json"
    $adminToken = $adminLoginResp.access_token
    Write-Host "PASSED: Admin Login Successful! ($($adminLoginResp.user.full_name))" -ForegroundColor Green
    
    # Provision Staff
    $staffId = "FAC-SRIT-$randomNum"
    $provisionBody = @{
        role_id = "ROLE_FACULTY"
        staff_id = $staffId
        email = "faculty$randomNum@srit.ac.in"
        initial_password = "FacultyPass@123"
        full_name = "Prof. Auto Faculty $randomNum"
        department = "CSE"
    } | ConvertTo-Json
    
    $headers = @{
        Authorization = "Bearer $adminToken"
    }
    
    $provResp = Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/provision" -Method Post -Body $provisionBody -ContentType "application/json" -Headers $headers
    Write-Host "PASSED: Admin Successfully Provisioned Staff Member!" -ForegroundColor Green
    Write-Host "  Provisioned User ID: $($provResp.user_id)" -ForegroundColor Green
    Write-Host "  Role: $($provResp.role_id)" -ForegroundColor Green
    
} catch {
    Write-Host "FAILED: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails) { Write-Host "Details: $($_.ErrorDetails.Message)" -ForegroundColor Red }
}

Write-Host "`n========================================================" -ForegroundColor Cyan
Write-Host "ALL TESTS COMPLETED" -ForegroundColor Cyan
Write-Host "========================================================`n" -ForegroundColor Cyan


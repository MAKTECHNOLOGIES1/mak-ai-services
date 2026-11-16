# =============================================================================
# Helper script to sync secrets to Cloudflare Workers via Wrangler
# Reads from local .env and uploads secrets securely
# =============================================================================

param (
    [string]$TargetEnv = "test"
)

$envFile = Join-Path $PSScriptRoot ".env"
if (-not (Test-Path $envFile)) {
    $envFile = Join-Path $PSScriptRoot "..\..\.env"
}

if (-not (Test-Path $envFile)) {
    Write-Error "Could not locate .env file."
    exit 1
}

Write-Host "Reading secrets from: $envFile" -ForegroundColor Cyan

# Read keys from .env
$secrets = @{}
Get-Content $envFile | ForEach-Object {
    $line = $_.Trim()
    if ($line -and -not $line.StartsWith("#") -and $line.Contains("=")) {
        $parts = $line.Split("=", 2)
        $key = $parts[0].Trim()
        $val = $parts[1].Trim()
        if ($val -ne "") {
            $secrets[$key] = $val
        }
    }
}

$keysToSync = @(
    "SUPABASE_SERVICE_KEY",
    "JWT_SECRET",
    "INTERNAL_SERVICE_KEY"
)

foreach ($k in $keysToSync) {
    if ($secrets.ContainsKey($k)) {
        $v = $secrets[$k]
        Write-Host "Setting Cloudflare secret: $k (Env: $TargetEnv)..." -ForegroundColor Yellow
        $v | npx wrangler secret put $k --env $TargetEnv
    } else {
        Write-Warning "Key $k not found or empty in .env"
    }
}

Write-Host "Secrets sync completed successfully." -ForegroundColor Green

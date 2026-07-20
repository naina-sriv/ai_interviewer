$ErrorActionPreference = "Stop"

Write-Host "Restructuring for Native Vercel Support..."

# Move backend into frontend/api
Move-Item -Path "ai_interview_service" -Destination "ai_interview_frontend\api"

# Rename main.py to index.py
Rename-Item -Path "ai_interview_frontend\api\main.py" -NewName "index.py"

# Create Vercel rewrite rules for FastAPI
$vercelJson = @"
{
  "rewrites": [
    { "source": "/api/(.*)", "destination": "/api/index.py" }
  ]
}
"@
Set-Content -Path "ai_interview_frontend\vercel.json" -Value $vercelJson

# Delete legacy vercel.json from root
Remove-Item -Path "vercel.json"

Write-Host "Done restructuring files."

$ErrorActionPreference = "Stop"

Write-Host "Reverting to side-by-side monorepo structure..."

# Move backend back to root
Move-Item -Path "ai_interview_frontend\api" -Destination "ai_interview_service"

# Rename index.py back to main.py
Rename-Item -Path "ai_interview_service\index.py" -NewName "main.py"

# Create legacy vercel.json at root
$vercelJson = @"
{
  "version": 2,
  "builds": [
    {
      "src": "ai_interview_frontend/package.json",
      "use": "@vercel/static-build"
    },
    {
      "src": "ai_interview_service/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "ai_interview_service/main.py"
    },
    {
      "src": "/(.*)",
      "dest": "ai_interview_frontend/`$1"
    }
  ]
}
"@
Set-Content -Path "vercel.json" -Value $vercelJson

# Delete the frontend vercel.json
if (Test-Path "ai_interview_frontend\vercel.json") {
    Remove-Item -Path "ai_interview_frontend\vercel.json"
}

Write-Host "Revert completed."

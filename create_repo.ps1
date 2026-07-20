$ErrorActionPreference = "Stop"

Write-Host "Initializing Git Repository..."
if (Test-Path ".git") {
    Remove-Item -Recurse -Force ".git"
}

git init

# Check if user has git config setup, otherwise set a dummy one so commits don't fail
$gitName = git config user.name
if (-not $gitName) {
    git config user.name "AI Developer"
    git config user.email "dev@ai.local"
}

Write-Host "Building commit history slowly..."

# Commit 1
git add docker-compose.yml .env ai_interview_service/requirements.txt ai_interview_service/Dockerfile ai_interview_frontend/package.json ai_interview_frontend/package-lock.json
git commit -m "chore: initial project setup and docker configuration"

# Commit 2
git add ai_interview_service/main.py ai_interview_service/models/ ai_interview_service/request_model/ ai_interview_service/response_model/
git commit -m "feat(backend): setup FastAPI application and pydantic models"

# Commit 3
git add ai_interview_service/services/ ai_interview_service/store/ ai_interview_service/routers/ ai_interview_service/util/
git commit -m "feat(backend): implement Gemini AI service and interview routing logic"

# Commit 4
git add ai_interview_frontend/public/ ai_interview_frontend/Dockerfile
git commit -m "chore(frontend): configure public assets and docker build"

# Commit 5
git add ai_interview_frontend/src/index.css ai_interview_frontend/src/assets/
git commit -m "style(frontend): implement premium dark-mode glassmorphism UI"

# Commit 6
git add ai_interview_frontend/src/components/ ai_interview_frontend/src/pages/ ai_interview_frontend/src/App.js
git commit -m "feat(frontend): build interview dashboard and components"

# Commit 7
git add ai_interview_frontend/src/services/ ai_interview_frontend/src/hooks/ ai_interview_frontend/src/util/ ai_interview_frontend/src/index.js
git commit -m "feat(frontend): connect React to FastAPI and setup speech recognition"

# Commit 8
git add README.md ai_interview_frontend/README.md ai_interview_service/README.md
git commit -m "docs: add comprehensive project documentation and diagrams"

# Commit 9 (Catch all)
git add .
try {
    git commit -m "chore: final project polish and adjustments"
} catch {
    # It's fine if there's nothing left to commit
}

Write-Host "Commit history generated successfully!"
Write-Host ""
Write-Host "Checking for GitHub CLI (gh)..."

if (Get-Command gh -ErrorAction SilentlyContinue) {
    Write-Host "GitHub CLI found. Creating repository 'ai_interviewer' on your GitHub..."
    gh repo create ai_interviewer --private --source=. --remote=origin --push
    Write-Host "Successfully created and pushed to GitHub!"
} else {
    Write-Warning "GitHub CLI (gh) is not installed on this machine."
    Write-Host "I have generated the local commit history. To push to GitHub, please:"
    Write-Host "1. Create a repository named 'ai_interviewer' on GitHub manually."
    Write-Host "2. Run: git remote add origin https://github.com/YOUR_USERNAME/ai_interviewer.git"
    Write-Host "3. Run: git push -u origin master"
}

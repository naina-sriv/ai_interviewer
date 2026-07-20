from fastapi import FastAPI
from routers.interview import router as interview_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    version="0.0.1",
    title="Smart AI Tech Interviewer API",
    description="Smart AI Interview Backend API"
)

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Local development route
app.include_router(interview_router)

# Vercel Serverless route
app.include_router(interview_router, prefix="/api")

"""
Drop into your FastAPI app's main.py (near app = FastAPI()).
Loads allowed origins from the backend .env so CORS is
environment-specific — no wildcard "*" in production.
"""

import os
from fastapi.middleware.cors import CORSMiddleware

allowed_origins = [
    origin.strip()
    for origin in os.environ.get("ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,   # exact deployed frontend domain(s), e.g. ["https://your-frontend.vercel.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

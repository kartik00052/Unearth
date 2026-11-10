from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Unearth API",
    description="Evidence-driven semantic discovery for AI agents.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "unearth-backend",
        "version": "0.1.0",
    }


@app.get("/", tags=["Root"])
def root():
    return {"message": "Welcome to Unearth API"}

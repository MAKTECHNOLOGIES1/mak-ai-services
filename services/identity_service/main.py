from fastapi import FastAPI

app = FastAPI(
    title="AMK Platform - identity_service",
    version="1.0.0",
    docs_url="/docs"
)

@app.get("/health")
async def health_check():
    return {"service": "identity_service", "status": "healthy"}

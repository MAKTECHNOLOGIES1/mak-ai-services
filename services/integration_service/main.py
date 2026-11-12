from fastapi import FastAPI

app = FastAPI(
    title="AMK Platform - integration_service",
    version="1.0.0",
    docs_url="/docs"
)

@app.get("/health")
async def health_check():
    return {"service": "integration_service", "status": "healthy"}

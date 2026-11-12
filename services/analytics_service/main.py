from fastapi import FastAPI

app = FastAPI(
    title="AMK Platform - analytics_service",
    version="1.0.0",
    docs_url="/docs"
)

@app.get("/health")
async def health_check():
    return {"service": "analytics_service", "status": "healthy"}

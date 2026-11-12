from fastapi import FastAPI

app = FastAPI(
    title="AMK Platform - audit_service",
    version="1.0.0",
    docs_url="/docs"
)

@app.get("/health")
async def health_check():
    return {"service": "audit_service", "status": "healthy"}

from fastapi import FastAPI

app = FastAPI(
    title="AMK Platform - api_gateway",
    version="1.0.0",
    docs_url="/docs"
)

@app.get("/health")
async def health_check():
    return {"service": "api_gateway", "status": "healthy"}

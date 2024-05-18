
from fastapi import FastAPI

app = FastAPI(
    title="app_name",
    description="API for app_name",
    verion="0.1.0",
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Local server"
        }
    ]
)
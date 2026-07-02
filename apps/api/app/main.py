from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(name=settings.PROJECT_NAME)


@app.get("/")
async def main():
    return {"message": "Hello, World!"}

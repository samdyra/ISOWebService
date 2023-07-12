from fastapi import FastAPI
from database import startup_db_client, shutdown_db_client
from bookstore.routes import router as book_router
from dotenv import dotenv_values
from mangum import Mangum

config = dotenv_values(".env")

app = FastAPI()

handler = Mangum(app)

@app.on_event("startup")
async def startup():
    startup_db_client(app, config)

@app.on_event("shutdown")
async def shutdown():
    shutdown_db_client(app)

app.include_router(book_router, tags=["books"], prefix="/book")


from fastapi import FastAPI
from config.database import startup_db_client, shutdown_db_client
from bookstore.routes import router as book_router
from s100.s102.routes import router as s102_router
from dotenv import dotenv_values

config = dotenv_values(".env")

app = FastAPI()

@app.on_event("startup")
async def startup():
    startup_db_client(app, config)

@app.on_event("shutdown")
async def shutdown():
    shutdown_db_client(app)

app.include_router(book_router, tags=["books"], prefix="/book")
app.include_router(s102_router, tags=["s102"], prefix="/s102")


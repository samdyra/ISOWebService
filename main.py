from fastapi import FastAPI
from dotenv import dotenv_values
from pymongo import MongoClient
from routes import router as book_router

config = dotenv_values(".env")

app = FastAPI()

@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient(config["ATLAS_URI"])
    app.database = app.mongodb_client[config["DB_NAME"]]
    # app.mongodb_client = MongoClient('mongodb+srv://dwisam001:dwisam001@isocluster.wfghllw.mongodb.net/?retryWrites=true&w=majority')
    # app.database = app.mongodb_client['ISOAPPSERVICE']

@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()

app.include_router(book_router, tags=["books"], prefix="/book")


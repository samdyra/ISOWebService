from pymongo import MongoClient


def startup_db_client(app, config):
    app.mongodb_client = MongoClient(config["ATLAS_URI"])
    app.database = app.mongodb_client[config["DB_NAME"]]



def shutdown_db_client(app):
    app.mongodb_client.close()
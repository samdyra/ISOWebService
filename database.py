from pymongo import MongoClient


def startup_db_client(app, config):
    app.mongodb_client = MongoClient('mongodb+srv://dwisam001:dwisam001@isocluster.wfghllw.mongodb.net/?retryWrites=true&w=majority')
    app.database = app.mongodb_client[config["ISOAPPSERVICE"]]

def shutdown_db_client(app):
    app.mongodb_client.close()
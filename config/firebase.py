import pyrebase
from dotenv import dotenv_values

config = dotenv_values(".env")


config = {
    "apiKey": config["FIREBASE_API_KEY"],
    "authDomain": config["FIREBASE_AUTH_DOMAIN"],
    "projectId": config["FIREBASE_PROJECT_ID"],
    "storageBucket": config["FIREBASE_STORAGE_BUCKET"],
    "messagingSenderId": config["FIREBASE_MESSAGING_SENDER_ID"],
    "appId": config["FIREBASE_APP_ID"],
    "databaseURL": config["FIREBASE_DATABASE_URL"]
}

firebase = pyrebase.initialize_app(config)

storage = firebase.storage()

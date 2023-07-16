import pyrebase

config = {
  "apiKey": "AIzaSyCIKis22qb5fDnkRABgfzm8zq2fi7yaI6E",
  "authDomain": "watermelongisapp.firebaseapp.com",
  "projectId": "watermelongisapp",
  "storageBucket": "watermelongisapp.appspot.com",
  "messagingSenderId": "429822291246",
  "appId": "1:429822291246:web:b5578743c899a029139ebf",
  "databaseURL": "https://watermelongisapp-default-rtdb.firebaseio.com/"
}

firebase = pyrebase.initialize_app(config)

storage = firebase.storage()
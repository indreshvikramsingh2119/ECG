import requests
import os
from dotenv import load_dotenv

load_dotenv()

FIREBASE_API_KEY = os.getenv('GOOGLE_API')

def save_user_info(local_id, user_data):
    db_url = f"https://ecg-authentication-70659.firebaseio.com/users/{local_id}.json"
    r = requests.put(db_url, json=user_data)
    return r.json() 

def sign_up(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    r = requests.post(url, json=payload)
    return r.json()

def sign_in(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    r = requests.post(url, json=payload)
    return r.json()

def get_firebase_user_info(local_id):
    db_url = f"https://ecg-authentication-70659.firebaseio.com/users/{local_id}.json"
    r = requests.get(db_url)
    if r.status_code == 200:
        return r.json()
    return None
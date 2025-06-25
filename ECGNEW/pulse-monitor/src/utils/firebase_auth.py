def sign_up(email, password):
    import requests

    url = "https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=YOUR_API_KEY"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(url, json=payload)
    return response.json()

def sign_in(email, password):
    import requests

    url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=YOUR_API_KEY"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(url, json=payload)
    return response.json()
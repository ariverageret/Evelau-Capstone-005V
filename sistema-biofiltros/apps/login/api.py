import requests
from apps.config.conexion import API_BASE_URL

class APIClient:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.token = None

    def login(self, username: str, password: str):
        url = f"{self.base_url}/auth/login"
        payload = {"username": username, "password": password}
        response = requests.post(url, json=payload)
        try:
            data = response.json()
        except ValueError:
            return {"error": f"Respuesta inválida del servidor: {response.text}"}

        if response.status_code == 200 and "access_token" in data:
            self.token = data["access_token"]
            return data
        return {"error": data}

    def me(self):
        if not self.token:
            return {"error": "No hay token, haz login primero"}
        
        url = f"{self.base_url}/auth/me?token={self.token}"  # token como query param
        response = requests.get(url)
        try:
            data = response.json()
        except ValueError:
            return {"error": f"Respuesta inválida del servidor: {response.text}"}

        if response.status_code == 200:
            return data
        return {"error": data}

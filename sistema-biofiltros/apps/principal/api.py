from apps.config.conexion import API_BASE_URL
import requests


class APIClient:
    def __init__(self):
        self.base_url = API_BASE_URL
        
    
    def get_eficiencia(self):
        url = f"{self.base_url}/eficiencia"
        response = requests.get(url)
        try:
            data = response.json()
        except ValueError:
            return {"error": f"Respuesta inválida del servidor: {response.text}"}
        if response.status_code == 200:
            return data
        return {"error": data}
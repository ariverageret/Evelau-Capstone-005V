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
    
    def get_lecturas(self):
        url = f"{self.base_url}/lecturas-sensores/lecturas-sensores?skip=0&limit=999999999"
        response = requests.get(url)
        try:
            data = response.json()
        except ValueError:
            return {"error": f"Respuesta inválida del servidor: {response.text}"}
        if response.status_code == 200:
            return data
        return {"error": data}
    
    def predicciones(self, datos):
        url = f"{self.base_url}/predictions/cumplimiento"
        try:
            response = requests.post(url, json=datos)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Error en la solicitud: {str(e)}"}


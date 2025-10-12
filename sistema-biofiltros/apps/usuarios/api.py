import requests
from apps.config.conexion import API_BASE_URL

class APIClient:
    def __init__(self):
        self.base_url = API_BASE_URL
        
    def get_Users(self):
        url = f"{self.base_url}/usuarios/GetUsuarios"
        response = requests.get(url)
        try:
            data = response.json()
        except ValueError:
            return {"error": f"Respuesta inválida del servidor: {response.text}"}

        if response.status_code == 200:
            return data
        return {"error": data}
    
    def create_User(self, username: str, email: str, password: str, rol: str):
        url = f"{self.base_url}/usuarios/addUsuario"
        payload = {"username": username, "email": email, "password_hash": password, "rol": rol}
        response = requests.post(url, json=payload)
        try:
            data = response.json()
        except ValueError:
            return {"error": f"Respuesta inválida del servidor: {response.text}"}

        # Considera 200 o 201 como éxito
        if response.status_code in [200, 201]:
            return data

        # Solo si es otro código, lo tomamos como error
        return {"error": data}

    
    def update_User(self, user_id: int, username: str = None, email: str = None, rol: str = None, password: str = None, estado: str = None):
        url = f"{self.base_url}/usuarios/ModificarUsuario"
        payload = {"id_usuario": user_id}

        if username:
            payload["username"] = username
        if email:
            payload["email"] = email
        if rol:
            payload["rol"] = rol
        if password:
            payload["password_hash"] = password
        if estado:
            payload["estado"] = estado

        response = requests.post(url, json=payload)
        try:
            data = response.json()
        except ValueError:
            return {"error": f"Respuesta inválida del servidor: {response.text}"}

        if response.status_code in (200, 201):
            return data
        return {"error": data}

    
    def get_Roles(self):
        url = f"{self.base_url}/roles/GetRoles"
        response = requests.get(url)
        try:
            data = response.json()
        except ValueError:
            return {"error": f"Respuesta inválida del servidor: {response.text}"}

        if response.status_code == 200:
            return data
        return {"error": data}
    
    def create_Role(self, nombre_rol: str, descripcion: str):
        url = f"{self.base_url}/roles/addRol"
        payload = {"nombre_rol": nombre_rol, "descripcion": descripcion}
        response = requests.post(url, json=payload)
        try:
            data = response.json()
        except ValueError:
            return {"error": f"Respuesta inválida del servidor: {response.text}"}

        if response.status_code == 201:
            return data
        return {"error": data}
    
    def update_Role(self, role_id: int, nombre_rol: str = None, descripcion: str = None):
        url = f"{self.base_url}/roles/ModificarRol"
        payload = {"id_rol": role_id}

        if nombre_rol:
            payload["nombre_rol"] = nombre_rol
        if descripcion:
            payload["descripcion"] = descripcion

        response = requests.post(url, json=payload)
        try:
            data = response.json()
        except ValueError:
            return {"error": f"Respuesta inválida del servidor: {response.text}"}

        if response.status_code in (200, 201):
            return data
        return {"error": data}
    
    def delete_User(self, user_id: int):
        url = f"{self.base_url}/usuarios/DeleteUsuario/{user_id}"
        response = requests.delete(url)
        try:
            data = response.json()
        except ValueError:
            return {"error": f"Respuesta inválida del servidor: {response.text}"}

        if response.status_code == 200:
            return data
        return {"error": data}
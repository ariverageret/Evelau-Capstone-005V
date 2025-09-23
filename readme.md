
# Proyecto de monitoreo de biofiltros

Este es un proyecto de Python que utiliza un entorno virtual para gestionar las dependencias.

## Requisitos

- Python 1.13.7
- pip

## Configuración del Entorno Virtual

1. Asegúrate de tener Python 1.13.7 instalado en tu sistema. Puedes descargarlo desde [aquí](https://www.python.org/downloads/release/python-137/).
2. Crea un entorno virtual en el directorio del proyecto:
   ```bash
   python1.13.7 -m venv venv
   ```
3. Activa el entorno virtual:
   - En Windows:
     ```bash
     venv\Scripts\activate
     ```
   - En macOS y Linux:
     ```bash
     source venv/bin/activate
     ```
4. Instala las dependencias del proyecto utilizando el archivo `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

Una vez que el entorno virtual esté activado y las dependencias instaladas, puedes ejecutar tu proyecto de la siguiente manera:

```bash
python manage.py
```

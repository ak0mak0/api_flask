from app import create_app

# Importar la configuración de desarrollo desde config.py
from config import DevelopmentConfig

# Obtener la aplicación Flask creada con la función create_app
app = create_app(DevelopmentConfig)

# Punto de entrada de la aplicación
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8160)

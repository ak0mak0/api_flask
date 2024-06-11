# config.py

class Config:
    SECRET_KEY = 'akmak2470'  # Cambia esto por una clave secreta única
    MONGODB_USERNAME = 'akmak_1'
    MONGODB_PASSWORD = 'xxWarWtqO5vVRgso'
    MONGODB_CLUSTER = 'cluster0.glb67p5.mongodb.net'
    MONGODB_DBNAME = 'proyectodb'
    
class DevelopmentConfig(Config):
    DEBUG = True
    ENV = 'development'

class ProductionConfig(Config):
    DEBUG = False
    ENV = 'production'
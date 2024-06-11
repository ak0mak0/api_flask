from pymongo import MongoClient, errors
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId

def get_db():
    # Obtener la configuración de la aplicación Flask
    config = current_app.config

    # Construir la URI de conexión utilizando los valores de la configuración
    username = config['MONGODB_USERNAME']
    password = config['MONGODB_PASSWORD']
    cluster = config['MONGODB_CLUSTER']
    dbname = config['MONGODB_DBNAME']
    uri = f"mongodb+srv://{username}:{password}@{cluster}/{dbname}?retryWrites=true&w=majority"

    # Establecer la conexión con MongoDB Atlas
    client = MongoClient(uri)

    # Devolver el objeto de base de datos
    return client[dbname]




# obtiene ultimo valor en counters para generar un id incremental
def get_next_sequence_value(sequence_name):
    db = get_db()
    counter = db.counters.find_one_and_update(
        {"_id": sequence_name},
        {"$inc": {"sequence_value": 1}},
        return_document=True
    )
    return counter["sequence_value"]



# Verifica que la colecion sitios y counters exista, sino crea una nueva
def create_collection_sitios():
    db = get_db()
    if "sitios" not in db.list_collection_names():
        try:
            db.create_collection("sitios", validator={
                '$jsonSchema': {
                    'bsonType': 'object',
                    'required': ["nombre_sitio", "latitud", "longitud", ],
                    'properties': {
                        'nombre_sitio': {
                            'bsonType': 'string',
                            'description': "Debe ser una cadena de caracteres para el nombre del sitio."
                        },
                        'latitud': {
                            'bsonType': 'double',
                            'description': "Debe ser un número flotante para la latitud."
                        },
                        'longitud': {
                            'bsonType': 'double',
                            'description': "Debe ser un número flotante para la longitud."
                        },
                    }
                }
            })
        except errors.CollectionInvalid:
            pass

    if "counters" not in db.list_collection_names():
        db.create_collection("counters")

    if db.counters.find_one({"_id": "sitioid"}) is None:
        db.counters.insert_one({"_id": "sitioid", "sequence_value": 0})


        
def create_collection_users():
    db = get_db()
    if "usuarios" not in db.list_collection_names():
        # Crear la colección "usuarios" si no existe
        db.create_collection("usuarios", validator={
            '$jsonSchema': {
                'bsonType': 'object',
                'required': ["username", "password", "name"],
                'properties': {
                    'username': {
                        'bsonType': 'string',
                        'description': "Debe ser una cadena de caracteres para el nombre de usuario."
                    },
                    'password': {
                        'bsonType': 'string',
                        'description': "Debe ser una cadena de caracteres para la contraseña."
                    },
                    'name': {
                        'bsonType': 'string',
                        'description': "Debe ser una cadena de caracteres para el nombre del usuario."
                    }
                }
            }
        })
     
# Clase User para manejar los usuarios
class User:
    def __init__(self, id, username, name, password):
        self.id = str(id)
        self.username = username
        self.name = name
        self.password = password
    
    def save(self):
        db = get_db()
        db.usuarios.insert_one({
            "username": self.username,
            "name": self.name,
            "password": self.password
        })
    
    def get_id(self):
        return self.id
    
    @staticmethod
    def get(id):
        db = get_db()
        user = db.usuarios.find_one({'_id': ObjectId(id)})
        if user:
            return User(user["_id"], user["username"], user["name"], user["password"])
        return None
    
    @staticmethod
    def find_by_username(username):
        db = get_db()
        user = db.usuarios.find_one({"username": username})
        if user:
            return User(user["_id"], user["username"], user["name"], user["password"])
        return None
    
    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False

    def check_password(self, password):
        return check_password_hash(self.password, password)
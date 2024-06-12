from pymongo import MongoClient, errors
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId

class MongoDBManager:
    def __init__(self):
        self.client = None
        self.db = None

    def connect(self):
        # Obtener la configuración de la aplicación Flask
        config = current_app.config

        # Construir la URI de conexión utilizando los valores de la configuración
        username = config['MONGODB_USERNAME']
        password = config['MONGODB_PASSWORD']
        cluster = config['MONGODB_CLUSTER']
        dbname = config['MONGODB_DBNAME']
        uri = f"mongodb+srv://{username}:{password}@{cluster}/{dbname}?retryWrites=true&w=majority"

        # Establecer la conexión con MongoDB Atlas
        self.client = MongoClient(uri)
        self.db = self.client[dbname]

    def get_db(self):
        if not self.db:
            self.connect()
        return self.db

    def create_collection(self, name, validator=None):
        db = self.get_db()
        if name not in db.list_collection_names():
            try:
                db.create_collection(name, validator=validator)
            except errors.CollectionInvalid:
                pass

class UserManager:
    def __init__(self, mongodb_manager):
        self.db_manager = mongodb_manager
        self.create_collection_users()

    def create_collection_users(self):
        validator = {
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
        }
        self.db_manager.create_collection("usuarios", validator=validator)

from bson import ObjectId

class User:
    def __init__(self, username, password, name, _id=None):
        self._id = _id
        self.username = username
        self.password = generate_password_hash(password)
        self.name = name

    def save(self):
        db = MongoDBManager().get_db()
        users_collection = db["usuarios"]
        user_data = {
            "username": self.username,
            "password": self.password,
            "name": self.name
        }
        result = users_collection.insert_one(user_data)
        self._id = result.inserted_id  # Asignar el _id generado al objeto User

    @staticmethod
    def find_by_username(username):
        db = MongoDBManager().get_db()
        users_collection = db["usuarios"]
        return users_collection.find_one({"username": username})

    def check_password(self, password):
        return check_password_hash(self.password, password)

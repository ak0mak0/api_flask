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

# Modelos para recomendaciones
class Usuario:
    def __init__(self, user_id, nombre, preferencias):
        self.user_id = user_id
        self.nombre = nombre
        self.preferencias = preferencias
    
    @classmethod
    def from_json(cls, json_data):
        if json_data:
            return cls(
                user_id = json_data.get('_id'),
                nombre = json_data.get('name'),
                preferencias = json_data.get('preferencias', [])
            )
        return None
    
    @classmethod
    def find_by_id(cls, user_id):
        db = MongoDBManager().get_db()
        users_collection = db["usuarios"]
        usuario = users_collection.find_one({'_id': user_id})
        if usuario:
            return Usuario(usuario['_id'], usuario['name'], usuario['preferencias'])
        return None
    
class Sitio:
    def __init__(self, nombre_sitio, latitud, longitud, descripcion=None, categorias = None, calificacion_promedio=None):
        self.nombre_sitio = nombre_sitio
        self.latitud = latitud
        self.longitud = longitud
        self.descripcion = descripcion
        self.categorias = categorias
        self.calificacion_promedio = calificacion_promedio

    @classmethod
    def from_json(cls, json_data):
        db = MongoDBManager().get_db()
        if(json_data is None):
            return None
        nombre = json_data.get('nombre')
        collectionSitios = db['sitios']
        sitio = collectionSitios.find_one({'nombre': nombre})
        if(sitio is None):
            return None
        return cls(
            nombre_sitio = sitio.get('nombre'),
            latitud = sitio.get('latitud'),
            longitud = sitio.get('longitud'),
            descripcion = sitio.get('descripcion'),
            categorias = sitio.get('categorias'),
            calificacion_promedio = sitio.get('calificacion_promedio'),
        )

    def to_json(self):
        return {
            'nombre_sitio': self.nombre_sitio,
            'latitud': self.latitud,
            'longitud': self.longitud,
            'descripcion': self.descripcion,
            'categorias': self.categorias,
        }
    
    @classmethod
    def find_by_name(cls, nombre_sitio):
        db = MongoDBManager().get_db()
        collectionSitios = db['sitios']
        sitio = collectionSitios.find_one({'nombre': nombre_sitio})
        if sitio:
            return Sitio(sitio['nombre'], sitio['latitud'], sitio['longitud'], sitio['descripcion'], sitio['categorias'])
        return None
    
class Categoria ():
    def __init__(self, nombre_categoria, descripcion):
        self.nombre_categoria = nombre_categoria
        self.descripcion = descripcion

    @classmethod
    def from_json(cls, json_data):
        return cls(
            nombre_categoria=json_data.get('nombre_categoria'),
            descripcion=json_data.get('descripcion')
        )

    def to_json(self):
        return {
            'nombre_categoria': self.nombre_categoria,
            'descripcion': self.descripcion
        }
    
class Recomendacion ():
    def __init__(self, usuario, sitio):
        self.usuario = usuario
        self.sitio = sitio
    def to_json(self):
        return {
            self.usuario.to_json(),
            self.sitio.to_json()
        }


class Review ():
    def __init__(self, user_id, sitio_id, calificacion, comentario):
        self.user_id = user_id
        self.sitio_id = sitio_id
        self.calificacion = calificacion
        self.comentario = comentario

    @classmethod
    def from_json(cls, json_data):
        return cls(
            user_id=json_data.get('user_id'),
            sitio_id=json_data.get('sitio_id'),
            calificacion=json_data.get('calificacion'),
            comentario=json_data.get('comentario')
        )

    def to_json(self):
        return {
            'user_id': self.user_id,
            'sitio_id': self.sitio_id,
            'calificacion': self.calificacion,
            'comentario': self.comentario
        }
    
class SistemaRecomendacion:
    def __init__(self, json_sitio, json_usuario = None):
        self.sitio_actual = Sitio.from_json(json_sitio)
        self.usuario = Usuario.from_json(json_usuario)
        self.recomendaciones = []

    def generar_recomendacion(self):
        db = MongoDBManager().get_db()
        collectionSitios = db['sitios']
        sitios_recomendados = collectionSitios.find({
            'categorias': {'$in': self.sitio_actual.categorias},
            'nombre': {'$ne': self.sitio_actual.nombre_sitio}
        }).sort([('calificacion_promedio', -1)]).limit(5)
        
        sitios_recomendados = list(sitios_recomendados)
        
        for sitio in sitios_recomendados:
            sitioObj = Sitio.find_by_name(sitio['nombre'])
            self.recomendaciones.append(Recomendacion(self.usuario, sitioObj))

        retorno = []
        for recomendacion in self.recomendaciones:
            site_json = recomendacion.sitio.to_json()
            retorno.append(site_json)

        return retorno

    def get_recomendaciones(self):
        return self.recomendaciones
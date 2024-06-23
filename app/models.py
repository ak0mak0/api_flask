from pymongo import MongoClient, errors
from flask import current_app
from bson.objectid import ObjectId
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from math import radians, sin, cos, sqrt, atan2


# ----------MANAGER CLASS----------
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
        if self.db is None:
            self.connect()
        return self.db

    def create_collection(self, name, validator=None):
        db = self.get_db()
        if name not in db.list_collection_names():
            try:
                db.create_collection(name, validator=validator)
            except errors.CollectionInvalid:
                pass

    def delete_collection(self, name):
        db = self.get_db()
        if name in db.list_collection_names():
            db[name].drop()

class UserManager:
    def __init__(self, mongodb_manager):
        self.db_manager = mongodb_manager
        self.reset_users_collection()

    def reset_users_collection(self):
        self.db_manager.delete_collection("usuarios")
        validator = {
            '$jsonSchema': {
                'bsonType': 'object',
                'required': ["nombre", "password", "email", "estado", "usuario_creacion", "es_administrador", "fecha_creacion"],
                'properties': {
                    'nombre': {
                        'bsonType': 'string',
                        'description': "Debe ser una cadena de caracteres para el nombre de usuario."
                    },
                    'password': {
                        'bsonType': 'string',
                        'description': "Debe ser una cadena de caracteres para la contraseña."
                    },
                    'email': {
                        'bsonType': 'string',
                        'description': "Debe ser una cadena de caracteres para el email."
                    },
                    'estado': {
                        'bsonType': 'string',
                        'description': "Debe ser una cadena de caracteres para el estado."
                    },
                    'usuario_creacion': {
                        'bsonType': 'string',
                        'description': "Debe ser una cadena de caracteres para el usuario de creación."
                    },
                    'es_administrador': {
                        'bsonType': 'bool',
                        'description': "Debe ser un booleano para indicar si el usuario es administrador."
                    },
                    'fecha_creacion': {
                        'bsonType': 'date',
                        'description': "Debe ser una fecha de creación."
                    }
                }
            }
        }
        self.db_manager.create_collection("usuarios", validator=validator)

class SitiosManager:
    def __init__(self, mongodb_manager):
        self.db_manager = mongodb_manager
        self.reset_sitios_collection()

    def reset_sitios_collection(self):
        self.db_manager.delete_collection("sitios")
        validator = {
            '$jsonSchema': {
                'bsonType': 'object',
                'required': ["nombre", "descripcion", "detalles", "categorias", "latitud", "longitud", "cant_visitas", "cant_likes", "calificacion_promedio", "cant_calificaciones", "reseñas", "estado", "fecha_creacion", "ultimo_ingreso", "usuario_creacion"],
                'properties': {
                    '_id': {'bsonType': 'objectId'},
                    'nombre': {'bsonType': 'string'},
                    'descripcion': {'bsonType': 'string'},
                    'detalles': {'bsonType': 'string'},
                    'categorias': {'bsonType': 'array'},
                    'latitud': {'bsonType': 'double'},
                    'longitud': {'bsonType': 'double'},
                    'cant_visitas': {'bsonType': 'int'},
                    'cant_likes': {'bsonType': 'int'},
                    'calificacion_promedio': {'bsonType': 'double'},
                    'cant_calificaciones': {'bsonType': 'int'},
                    'reseñas': {'bsonType': 'array'},
                    'estado': {'bsonType': 'string'},
                    'fecha_creacion': {'bsonType': 'date'},
                    'ultimo_ingreso': {'bsonType': 'date'},
                    'usuario_creacion': {'bsonType': 'string'}
                }
            }
        }
        self.db_manager.create_collection("sitios", validator=validator)

class ReviewsManager:
    def __init__(self, mongodb_manager):
        self.db_manager = mongodb_manager
        self.reset_reviews_collection()

    def reset_reviews_collection(self):
        self.db_manager.delete_collection("reviews")
        validator = {
            '$jsonSchema': {
                'bsonType': 'object',
                'required': ["_id", "id_usuario", "id_sitio", "opinion", "calificacion", "like", "visito", "fecha"],
                'properties': {
                    '_id': {
                        'bsonType': 'objectId',
                        'description': "ID de la reseña."
                    },
                    'id_usuario': {
                        'bsonType': 'objectId',
                        'description': "ID del usuario."
                    },
                    'id_sitio': {
                        'bsonType': 'objectId',
                        'description': "ID del sitio."
                    },
                    'opinion': {
                        'bsonType': 'string',
                        'description': "Opinión del usuario respecto al sitio."
                    },
                    'calificacion': {
                        'bsonType': 'int',
                        'description': "Calificación dada por el usuario al sitio."
                    },
                    'like': {
                        'bsonType': 'bool',
                        'description': "Indica si el usuario dio like al sitio."
                    },
                    'visito': {
                        'bsonType': 'bool',
                        'description': "Indica si el usuario visitó el sitio."
                    },
                    'fecha': {
                        'bsonType': 'date',
                        'description': "Fecha de última interacción con el sitio."
                    }
                }
            }
        }
        self.db_manager.create_collection("reviews", validator=validator)

class RecosSitiosManager:
    def __init__(self, mongodb_manager):
        self.db_manager = mongodb_manager
        self.reset_recos_sitios_collection()

    def reset_recos_sitios_collection(self):
        self.db_manager.delete_collection("recos_sitios")
        validator = {
            '$jsonSchema': {
                'bsonType': 'object',
                'required': ["_id", "_idsitio", "sitios_cercanos", "sitios_parecidos"],
                'properties': {
                    '_id': {
                        'bsonType': 'objectId',
                        'description': "ID de la reseña."
                    },
                    '_idsitio': {
                        'bsonType': 'objectId',
                        'description': "ID del sitio al que pertenecen las recomendaciones."
                    },
                    'sitios_cercanos': {
                        'bsonType': 'array',
                        'description': "IDs de sitios cercanos."
                    },
                    'sitios_parecidos': {
                        'bsonType': 'array',
                        'description': "IDs de sitios parecidos."
                    }
                }
            }
        }
        self.db_manager.create_collection("recos_sitios", validator=validator)

        
        
# ----------MODELS CLASS----------
# CLASE CON METODOS PARA MANIPULAR USUSARIOS
class Usuario:
    def __init__(self, nombre, password=None, email=None, estado=None, usuario_creacion=None, es_administrador=None, fecha_creacion=None, _id=None, password_hash=None):
        self._id = _id
        self.nombre = nombre
        if password:
            self.set_password(password)
        elif password_hash:
            self.password_hash = password_hash
        self.email = email
        self.estado = estado if estado else "inactivo"
        self.usuario_creacion = usuario_creacion if usuario_creacion else "AppLugares"
        self.es_administrador = es_administrador if es_administrador is not None else False
        self.fecha_creacion = fecha_creacion if fecha_creacion else datetime.now()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def update_estado(self, new_estado):
        db = MongoDBManager().get_db()
        users_collection = db["usuarios"]
        users_collection.update_one({'_id': self._id}, {'$set': {'estado': new_estado}})
        self.estado = new_estado

    @classmethod
    def find_by_name(cls, nombre):
        db = MongoDBManager().get_db()
        users_collection = db["usuarios"]
        usuario = users_collection.find_one({'nombre': nombre})
        if usuario:
            return cls(
                nombre=usuario['nombre'],
                password_hash=usuario['password'],  # Hashed password
                email=usuario['email'],
                estado=usuario['estado'],
                usuario_creacion=usuario['usuario_creacion'],
                es_administrador=usuario['es_administrador'],
                fecha_creacion=usuario['fecha_creacion'],
                _id=usuario['_id']  # Pasamos el ID aquí
            )
        return None

    def save(self):
        db = MongoDBManager().get_db()
        users_collection = db["usuarios"]

        user_data = {
            'nombre': self.nombre,
            'password': self.password_hash,  # Utilizamos el hash de la contraseña
            'email': self.email,
            'estado': self.estado,
            'usuario_creacion': self.usuario_creacion,
            'es_administrador': self.es_administrador,
            'fecha_creacion': self.fecha_creacion
        }

        if self._id:
            users_collection.update_one({'_id': self._id}, {'$set': user_data})
        else:
            result = users_collection.insert_one(user_data)
            self._id = result.inserted_id
    
    def to_dict(self):
        return {
            "_id": str(self._id),
            "nombre": self.nombre,
            "email": self.email,
            "estado": self.estado,
            "usuario_creacion": self.usuario_creacion,
            "es_administrador": self.es_administrador,
            "fecha_creacion": self.fecha_creacion
        }

    @classmethod
    def find_by_id(cls, user_id):
        db = MongoDBManager().get_db()
        user_data = db["usuarios"].find_one({"_id": user_id})
        if user_data:
            return cls(**user_data)
        return None
    
    
# CLASE CON METODOS PARA MANIPULAR LOS SITIOS
class Sitio:
    def __init__(self, nombre, descripcion, detalles, categorias, latitud, longitud, _id=None, cant_visitas=0, cant_likes=0, calificacion_promedio=0.0, cant_calificaciones=0, reseñas=None, estado="activo", fecha_creacion=None, ultimo_ingreso=None, usuario_creacion="API"):
        self._id = _id if _id else None
        self.nombre = nombre
        self.descripcion = descripcion
        self.detalles = detalles
        self.categorias = categorias
        self.latitud = latitud
        self.longitud = longitud
        self.cant_visitas = cant_visitas
        self.cant_likes = cant_likes
        self.calificacion_promedio = calificacion_promedio
        self.cant_calificaciones = cant_calificaciones
        self.reseñas = reseñas if reseñas else []
        self.estado = estado
        self.fecha_creacion = fecha_creacion if fecha_creacion else datetime.now()
        self.ultimo_ingreso = ultimo_ingreso if ultimo_ingreso else self.fecha_creacion
        self.usuario_creacion = usuario_creacion
    
    def get_top_visited_sites():
        db = MongoDBManager().get_db()
        sitios_collection = db["sitios"]
        top_sitios = sitios_collection.find().sort("cant_visitas", -1).limit(4)
        return list(top_sitios)
    
    @staticmethod
    def get_top_liked_sites():
        db = MongoDBManager().get_db()
        sitios_collection = db["sitios"]
        top_sitios = sitios_collection.find().sort("cant_likes", -1).limit(4)
        top_sitios_ids = [str(sitio['_id']) for sitio in top_sitios]
        return top_sitios_ids

    @staticmethod
    def get_all_sites():
        db = MongoDBManager().get_db()
        sitios_collection = db["sitios"]
        sitios = list(sitios_collection.find({}, {"nombre": 1}))  # Proyectamos solo el campo 'nombre'
        return sitios

    @classmethod
    def from_json(cls, data):
        nombre = data.get("nombre")
        descripcion = data.get("descripcion")
        detalles = data.get("detalles")
        categorias = data.get("categorias")
        latitud = data.get("latitud")
        longitud = data.get("longitud")

        if not all([nombre, descripcion, detalles, categorias, latitud, longitud]):
            raise ValueError("Faltan campos obligatorios en los datos JSON")

        return cls(nombre, descripcion, detalles, categorias, latitud, longitud)

    @classmethod
    def find_by_id(cls, sitio_id):
        db = MongoDBManager().get_db()
        sitio_data = db["sitios"].find_one({"_id": sitio_id})
        if sitio_data:
            return cls(**sitio_data)
        return None

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "detalles": self.detalles,
            "categorias": self.categorias,
            "latitud": self.latitud,
            "longitud": self.longitud,
            "cant_visitas": self.cant_visitas,
            "cant_likes": self.cant_likes,
            "calificacion_promedio": self.calificacion_promedio,
            "cant_calificaciones": self.cant_calificaciones,
            "reseñas": self.reseñas,
            "estado": self.estado,
            "fecha_creacion": self.fecha_creacion,
            "ultimo_ingreso": self.ultimo_ingreso,
            "usuario_creacion": self.usuario_creacion
        }

    def agregar_sitio(self):
        db = MongoDBManager().get_db()
        sitios_collection = db["sitios"]

        sitio_data = self.to_dict()

        result = sitios_collection.insert_one(sitio_data)
        self._id = result.inserted_id

        return self._id

# CLASE CON METODOS PARA MANIPULAR LAS REVIEWS
class Review:
    def __init__(self, id_usuario, id_sitio):
        self._id = None  # El _id será asignado automáticamente por la base de datos
        self.id_usuario = ObjectId(id_usuario)
        self.id_sitio = ObjectId(id_sitio)
        self.opinion = ""
        self.calificacion = 6
        self.like = False
        self.visito = False
        self.fecha = datetime.now()

    def save(self):
        db_manager = MongoDBManager()
        db = db_manager.get_db()
        reviews_collection = db["reviews"]

        review_data = {
            "id_usuario": self.id_usuario,
            "id_sitio": self.id_sitio,
            "opinion": self.opinion,
            "calificacion": self.calificacion,
            "like": self.like,
            "visito": self.visito,
            "fecha": self.fecha
        }

        result = reviews_collection.insert_one(review_data)
        self._id = result.inserted_id

    def find_existing_review(self):
        db_manager = MongoDBManager()
        db = db_manager.get_db()
        reviews_collection = db["reviews"]
        existing_review = reviews_collection.find_one({"id_usuario": self.id_usuario, "id_sitio": self.id_sitio})
        return existing_review

    def register(self):
        db_manager = MongoDBManager()
        db = db_manager.get_db()
        reviews_collection = db["reviews"]

        # Verificar si ya existe una combinación de id_usuario e id_sitio
        existing_review = self.find_existing_review()
        if existing_review:
            # Si ya existe, marcar visito como true
            reviews_collection.update_one(
                {"_id": existing_review["_id"]},
                {"$set": {"visito": True}}
            )
        else:
            # Si no existe, guardar la nueva reseña y marcar visito como true
            self.visito = True
            self.save()

    def add_like(self):
        db_manager = MongoDBManager()
        db = db_manager.get_db()
        reviews_collection = db["reviews"]
        sitios_collection = db["sitios"]

        # Buscar la reseña existente
        existing_review = self.find_existing_review()
        if existing_review:
            current_like = existing_review.get('like', False)
            if current_like:
                # Si el like es True, disminuir cant_likes del sitio y marcar like como False
                sitios_collection.update_one(
                    {"_id": self.id_sitio},
                    {"$inc": {"cant_likes": -1}}
                )
                reviews_collection.update_one(
                    {"_id": existing_review["_id"]},
                    {"$set": {"like": False}}
                )
            else:
                # Si el like es False, aumentar cant_likes del sitio y marcar like como True
                sitios_collection.update_one(
                    {"_id": self.id_sitio},
                    {"$inc": {"cant_likes": 1}}
                )
                reviews_collection.update_one(
                    {"_id": existing_review["_id"]},
                    {"$set": {"like": True}}
                )

    def add_qualifi(self, valor):
        db_manager = MongoDBManager()
        db = db_manager.get_db()
        reviews_collection = db["reviews"]
        sitios_collection = db["sitios"]

        # Buscar la reseña existente
        existing_review = self.find_existing_review()
        if existing_review:
            sitio = sitios_collection.find_one({"_id": self.id_sitio})
            if not sitio:
                raise ValueError("El sitio no existe.")

            if existing_review.get('calificacion', 6) == 6:
                # Si la calificación es 6 (sin calificar)
                cant_calificaciones = sitio.get('cant_calificaciones', 0)
                calificacion_promedio = sitio.get('calificacion_promedio', 0)
                nueva_calificacion_promedio = (calificacion_promedio * cant_calificaciones) + valor
                nueva_cant_calificaciones = cant_calificaciones + 1
                nueva_calificacion_promedio = nueva_calificacion_promedio / nueva_cant_calificaciones

                # Actualizar el sitio
                sitios_collection.update_one(
                    {"_id": self.id_sitio},
                    {
                        "$inc": {"cant_calificaciones": +1, "calificacion_promedio": -calificacion_promedio+nueva_calificacion_promedio}
                    }
                )
                # Actualizar la calificación de la reseña
                reviews_collection.update_one(
                    {"_id": existing_review["_id"]},
                    {"$set": {"calificacion": valor}}
                )
            else:
                # Si la calificación ya existe y no es 6
                cant_calificaciones = sitio.get('cant_calificaciones', 0)
                calificacion_promedio = sitio.get('calificacion_promedio', 0)
                calificacion_anterior = existing_review.get('calificacion', 0)
                nueva_calificacion_promedio = (calificacion_promedio * cant_calificaciones) - calificacion_anterior
                nueva_cant_calificaciones = cant_calificaciones - 1
                if nueva_cant_calificaciones != 0:
                    nueva_calificacion_promedio = nueva_calificacion_promedio / nueva_cant_calificaciones
                else:
                    nueva_calificacion_promedio = 0
                sitios_collection.update_one(
                    {"_id": self.id_sitio},
                    {
                        "$inc": {"cant_calificaciones": -1, "calificacion_promedio": -calificacion_promedio+nueva_calificacion_promedio}
                    }
                )
                # Actualizar la calificación de la reseña a 6 (sin calificar)
                reviews_collection.update_one(
                    {"_id": existing_review["_id"]},
                    {"$set": {"calificacion": 6}}
                )
        else:
            raise ValueError("No existe una reseña para esta combinación de usuario y sitio.")

class RecosSitio:
    def __init__(self, mongodb_manager):
        self.db_manager = mongodb_manager

    def find_nearest_sites(self, sitio_id):
        db = self.db_manager.get_db()
        sitios_collection = db["sitios"]
        sitio = sitios_collection.find_one({"_id": sitio_id})

        if sitio:
            sitios_cercanos = self.find_closest_sites(sitio, sitios_collection)
            sitios_parecidos = self.find_similar_sites(sitio, sitios_collection)

            reco = {
                "_idsitio": sitio_id,
                "sitios_cercanos": sitios_cercanos,
                "sitios_parecidos": sitios_parecidos
            }

            recos_sitios_collection = db["recos_sitios"]
            recos_sitios_collection.update_one({"_idsitio": sitio_id}, {"$set": reco}, upsert=True)

    def find_closest_sites(self, sitio, sitios_collection):
        sitios_cercanos = []
        for otro_sitio in sitios_collection.find():
            if otro_sitio["_id"] != sitio["_id"]:
                distancia = self.calculate_distance(sitio["latitud"], sitio["longitud"], otro_sitio["latitud"], otro_sitio["longitud"])
                sitios_cercanos.append({"_id": otro_sitio["_id"], "distancia": distancia})

        sitios_cercanos.sort(key=lambda x: x["distancia"])  # Ordenar por distancia
        sitios_cercanos = [sitio["_id"] for sitio in sitios_cercanos[:3]]  # Seleccionar los tres primeros
        return sitios_cercanos

    def find_similar_sites(self, sitio, sitios_collection):
        sitios_parecidos = []
        categorias_sitio = sitio["categorias"]
        sitios_encontrados = 0

        for otro_sitio in sitios_collection.find({"_id": {"$ne": sitio["_id"]}}):
            if sitios_encontrados >= 3:
                break

            if any(cat in categorias_sitio for cat in otro_sitio["categorias"]) and otro_sitio["_id"] not in sitios_parecidos:
                sitios_parecidos.append(otro_sitio["_id"])
                sitios_encontrados += 1

        return sitios_parecidos[:3]  # Limitar el número de sitios parecidos a 3

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        # Convertir grados a radianes
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        # Fórmula de Haversine
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = 6371 * c  # Radio de la Tierra en kilómetros
        return distance

    def get_sitios_cercanos(self, sitio_id):
        db = self.db_manager.get_db()
        recos_sitios_collection = db["recos_sitios"]
        sitio = recos_sitios_collection.find_one({"_idsitio": sitio_id})
        if sitio:
            cercanos = sitio.get("sitios_cercanos", [])
            formatted_results = [{"object_id": str(s["_id"]), "distancia": s["distancia"]} for s in cercanos]
            return formatted_results
        else:
            return []

    def get_sitios_parecidos(self, sitio_id):
        db = self.db_manager.get_db()
        recos_sitios_collection = db["recos_sitios"]
        sitio = recos_sitios_collection.find_one({"_idsitio": sitio_id})
        if sitio:
            return [str(s) for s in sitio.get("sitios_parecidos", [])]
        else:
            return []

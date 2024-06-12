from flask import Blueprint, jsonify, request
from app.models import MongoDBManager, UserManager, User, SistemaRecomendacion
from werkzeug.security import generate_password_hash
from bson import ObjectId

api_bp = Blueprint('api', __name__)

class UserHandler:
    @staticmethod
    def register():
        data = request.json
        required_fields = ["username", "password", "name"]

        if not all(field in data for field in required_fields):
            return jsonify({"error": "Datos incompletos"}), 400

        existing_user = User.find_by_username(data["username"])
        if existing_user is None:
            user = User(data["username"], data["password"], data["name"])
            user.save()
            user_info = {
                "_id": str(user._id),  # Se convierte a cadena para devolverlo en formato JSON
                "username": user.username,
                "password": user.password,
                "name": user.name,
            }
            return jsonify({"mensaje": "Usuario registrado con éxito", "usuario": user_info}), 201
        else:
            return jsonify({"error": "El usuario ya existe"}), 400

    @staticmethod
    def login():
        data = request.json
        required_fields = ["username", "password"]

        if not all(field in data for field in required_fields):
            return jsonify({"error": "Datos incompletos"}), 400

        user = User.find_by_username(data["username"])
        if user and user.check_password(data["password"]):
            return jsonify({"mensaje": "Inicio de sesión exitoso", "_id": str(user.id)}), 200
        else:
            return jsonify({"error": "Nombre de usuario o contraseña incorrectos"}), 401

class SitioHandler:
    @staticmethod
    def add_sitio():
        db_manager = MongoDBManager()
        db = db_manager.get_db()
        data = request.json

        if not data or not all(k in data for k in ("nombre_sitio", "latitud", "longitud")):
            return jsonify({"error": "Datos incompletos"}), 400

        nuevo_sitio = {
            "_id": ObjectId(),
            "nombre_sitio": data["nombre_sitio"],
            "latitud": data["latitud"],
            "longitud": data["longitud"]
        }

        try:
            db.sitios.insert_one(nuevo_sitio)
            nuevo_sitio['_id'] = str(nuevo_sitio['_id'])
            return jsonify({"mensaje": "Sitio agregado exitosamente", "sitio": nuevo_sitio}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    def get_sitio():
        data = request.get_json()
        sitio_id = data.get('_id')

        if not sitio_id:
            return jsonify({'error': 'El campo _id es obligatorio en el JSON'}), 400

        db_manager = MongoDBManager()
        db = db_manager.get_db()

        try:
            sitio = db.sitios.find_one({'_id': ObjectId(sitio_id)})
            if not sitio:
                return jsonify({'error': 'Sitio no encontrado'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500

        sitio_info = {
            '_id': str(sitio['_id']),
            'nombre': sitio['nombre'],
            'latitud': sitio['latitud'],
            'longitud': sitio['longitud']
        }
        return jsonify(sitio_info), 200

    @staticmethod
    def get_sitios():
        db_manager = MongoDBManager()
        db = db_manager.get_db()
        sitios = list(db.sitios.find())

        for sitio in sitios:
            sitio['_id'] = str(sitio['_id'])
        return jsonify({"sitios": sitios})

    @staticmethod
    def reset_all():
        db_manager = MongoDBManager()
        db = db_manager.get_db()
        db.sitios.delete_many({})
        return jsonify({"mensaje": "Todos los documentos en la colección 'sitios' han sido eliminados y el contador ha sido reiniciado"}), 200

class RecomendationHandler:
    @staticmethod
    def get_recomendacion():
        data = request.json
        sitio_actual = data.get('sitio')
        usuario = data.get('usuario')

        if not sitio_actual:
            return jsonify({'error': 'se requiere el sitio actual'}), 400
    
        sistema_recomendacion = SistemaRecomendacion(sitio_actual, usuario)
        recomendaciones = sistema_recomendacion.generar_recomendacion()

        return jsonify(recomendaciones)


api_bp.add_url_rule('/', view_func=lambda: 'Ejecutando API REST')
api_bp.add_url_rule('/register', view_func=UserHandler.register, methods=['POST'])
api_bp.add_url_rule('/login', view_func=UserHandler.login, methods=['POST'])
api_bp.add_url_rule('/addsitio', view_func=SitioHandler.add_sitio, methods=['POST'])
api_bp.add_url_rule('/getsitio', view_func=SitioHandler.get_sitio, methods=['POST'])
api_bp.add_url_rule('/sitios', view_func=SitioHandler.get_sitios, methods=['GET'])
api_bp.add_url_rule('/reset_all', view_func=SitioHandler.reset_all, methods=['POST'])
api_bp.add_url_rule('/recomendaciones', view_func=RecomendationHandler.get_recomendacion, methods=['POST'])
from flask import Blueprint, jsonify, request
from app.models import get_db, User
from werkzeug.security import generate_password_hash
from bson import ObjectId

# Crear un Blueprint para las rutas de la API
api_bp = Blueprint('api', __name__)

# Define una ruta inicial
@api_bp.route('/')
def home():
    return 'Ejecutando API REST'


# -----RUTAS PARA MANEJO DE USUARIOS-----

# Ruta para registrar un usuario
@api_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    required_fields = ["username", "password", "name"]

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Datos incompletos"}), 400

    existing_user = User.find_by_username(data["username"])
    if existing_user is None:
        hashed_password = generate_password_hash(data["password"])
        user_id = get_db().usuarios.insert_one({
            "username": data["username"],
            "name": data["name"],
            "password": hashed_password
        }).inserted_id
        user = User(user_id, data["username"], data["name"], hashed_password)
        return jsonify({"mensaje": "Usuario registrado con éxito", "_id": str(user_id)}), 201
    else:
        return jsonify({"error": "El usuario ya existe"}), 400

# Ruta para iniciar sesión
@api_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    required_fields = ["username", "password"]

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Datos incompletos"}), 400

    user = User.find_by_username(data["username"])
    if user and user.check_password(data["password"]):
        return jsonify({"mensaje": "Inicio de sesión exitoso", "_id": user.get_id()}), 200
    else:
        return jsonify({"error": "Nombre de usuario o contraseña incorrectos"}), 401



# -----RUTAS PARA MANEJO DE SITIOS-----

@api_bp.route('/addsitio', methods=['POST'])
def add_sitio():
    db = get_db()
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
        nuevo_sitio['_id'] = str(nuevo_sitio['_id'])  # Convertir ObjectId a string
        return jsonify({"mensaje": "Sitio agregado exitosamente", "sitio": nuevo_sitio}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/getsitio', methods=['POST'])
def get_sitio():
    data = request.get_json()
    sitio_id = data.get('_id')

    if not sitio_id:
        return jsonify({'error': 'El campo _id es obligatorio en el JSON'}), 400

    try:
        db = get_db()
        sitio = db.sitios.find_one({'_id': ObjectId(sitio_id)})
        if not sitio:
            return jsonify({'error': 'Sitio no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    sitio_info = {
        '_id': str(sitio['_id']),
        'nombre_sitio': sitio['nombre_sitio'],
        'latitud': sitio['latitud'],
        'longitud': sitio['longitud']
    }
    return jsonify(sitio_info), 200


# Ruta para obtener la lista de sitios
@api_bp.route('/sitios', methods=['GET'])
def get_sitios():
    db = get_db()
    sitios = list(db.sitios.find())
    return jsonify({"sitios": sitios})

# Ruta para resetear la colección sitios y counters
@api_bp.route('/reset_all', methods=['POST'])
def reset_all():
    db = get_db()
    
    # Eliminar todos los documentos de la colección "sitios"
    db.sitios.delete_many({})
    

    return jsonify({"mensaje": "Todos los documentos en la colección 'sitios' han sido eliminados y el contador ha sido reiniciado"}), 200


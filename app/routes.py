from flask import Blueprint, jsonify, request
from app.models import MongoDBManager, Usuario, UserManager, SitiosManager,Sitio, ReviewsManager, Review, RecosSitiosManager, RecosSitio
from bson import ObjectId

api_bp = Blueprint('api', __name__)

# RUTAS DE USUARIO
class UserHandler:
    @staticmethod
    def register():
        data = request.json
        required_fields = ["nombre", "password", "email"]

        if not all(field in data for field in required_fields):
            return jsonify({"error": "Datos incompletos"}), 400

        existing_user = Usuario.find_by_name(data["nombre"])
        if existing_user:
            return jsonify({"error": "Ya existe un usuario con este nombre"}), 400

        user = Usuario(
            nombre=data["nombre"],
            password=data["password"],
            email=data["email"]
        )
        user.save()

        user_info = {
            "_id": str(user._id),
            "nombre": user.nombre,
            "email": user.email,
            "estado": user.estado,
            "usuario_creacion": user.usuario_creacion,
            "es_administrador": user.es_administrador,
            "fecha_creacion": user.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')
        }
        return jsonify({"mensaje": "Usuario registrado con éxito", "usuario": user_info}), 201

    @staticmethod
    def login():
        data = request.json
        required_fields = ["nombre", "password"]

        if not all(field in data for field in required_fields):
            return jsonify({"error": "Datos incompletos"}), 400

        user = Usuario.find_by_name(data["nombre"])
        if user:
            if user.check_password(data["password"]):
                # Cambiar el estado a inactivo si ya estaba activo
                if user.estado == "activo":
                    user.update_estado("inactivo")
                    return jsonify({"mensaje": "Desconectado", "user_id": str(user._id)}), 200
                # Cambiar el estado a activo
                else:
                    user.update_estado("activo")
                    return jsonify({"mensaje": "Conectado", "user_id": str(user._id)}), 200
            else:
                return jsonify({"error": "Contraseña incorrecta"}), 401
        else:
            return jsonify({"error": "Usuario no encontrado"}), 404
    
    @staticmethod
    def getinfo():
        data = request.json
        user_id = data.get("user_id")

        if not user_id:
            return jsonify({"error": "Se requiere proporcionar el ID del usuario"}), 400

        try:
            user = Usuario.find_by_id(ObjectId(user_id))
            if user:
                return jsonify(user.to_dict()), 200
            else:
                return jsonify({"error": "Usuario no encontrado"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    
    @staticmethod
    def reset_users():
        db_manager = MongoDBManager()
        user_manager = UserManager(db_manager)
        return jsonify({"mensaje": "La colección de usuarios ha sido restablecida"}), 200


# RUTAS DE SITIOS
class SitioHandler:
    
    @staticmethod
    def reset_sitios():
        db_manager = MongoDBManager()
        sitio_manager = SitiosManager(db_manager)
        return jsonify({"mensaje": "Todos los documentos en la colección 'sitios' han sido eliminados y reiniciados"}), 200
    
    @staticmethod
    def new_sitio():
        data = request.get_json()
        try:
            nuevo_sitio = Sitio.from_json(data)
            sitio_id = nuevo_sitio.agregar_sitio()
            return jsonify({"mensaje": "Sitio creado exitosamente", "sitio_id": str(sitio_id)}), 201
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        
    @staticmethod
    def add_visit():
        data = request.json
        sitio_id = data.get('sitio_id')

        if not sitio_id:
            return jsonify({'error': 'Se requiere el ID del sitio'}), 400

        db_manager = MongoDBManager()
        db = db_manager.get_db()

        sitio = db.sitios.find_one({'_id': ObjectId(sitio_id)})
        if not sitio:
            return jsonify({'error': 'Sitio no encontrado'}), 404

        db.sitios.update_one({'_id': ObjectId(sitio_id)}, {'$inc': {'cant_visitas': 1}})
        return jsonify({'mensaje': 'Visita agregada exitosamente'}), 200


# RUTAS DE REVIEWS
class ReviewHandler:
    @staticmethod
    def reset_reviews():
        db_manager = MongoDBManager()
        reviews_manager = ReviewsManager(db_manager)
        return jsonify({"mensaje": "Todos los documentos en la colección 'reviews' han sido eliminados y reiniciados"}), 200

    @staticmethod
    def add_review():
        data = request.json
        
        # Extraer los datos necesarios del JSON
        id_usuario = data.get('id_usuario')
        id_sitio = data.get('id_sitio')
        
        # Crear una nueva instancia de Review
        new_review = Review(id_usuario, id_sitio)
        
        try:
            # Intentar guardar la nueva reseña
            new_review.save()
            return jsonify({"mensaje": "Reseña agregada exitosamente", "id_reseña": str(new_review._id)}), 201
        except ValueError as e:
            # Manejar el caso en el que ya exista una reseña para la misma combinación de id_usuario e id_sitio
            return jsonify({"error": str(e)}), 400 

    @staticmethod
    def register_visit():
        data = request.json

        # Extraer los datos necesarios del JSON
        id_usuario = data.get('id_usuario')
        id_sitio = data.get('id_sitio')

        # Verificar que los IDs de usuario y sitio sean válidos
        if not ObjectId.is_valid(id_usuario) or not ObjectId.is_valid(id_sitio):
            return jsonify({"error": "ID de usuario o sitio no válidos"}), 400

        # Crear una nueva instancia de Review
        new_review = Review(id_usuario, id_sitio)

        try:
            # Intentar registrar la visita
            new_review.register()
            return jsonify({"mensaje": "Visita registrada exitosamente"}), 201
        except ValueError as e:
            # Manejar errores en el registro de la visita
            return jsonify({"error": str(e)}), 400        

    @staticmethod
    def add_like():
        data = request.json

        # Extraer los datos necesarios del JSON
        id_usuario = data.get('id_usuario')
        id_sitio = data.get('id_sitio')

        # Verificar que los IDs de usuario y sitio sean válidos
        if not ObjectId.is_valid(id_usuario) or not ObjectId.is_valid(id_sitio):
            return jsonify({"error": "ID de usuario o sitio no válidos"}), 400

        # Crear una nueva instancia de Review
        review = Review(id_usuario, id_sitio)

        try:
            # Intentar agregar/quitar el like
            review.add_like()
            return jsonify({"mensaje": "Like actualizado exitosamente"}), 200
        except ValueError as e:
            # Manejar errores en la actualización del like
            return jsonify({"error": str(e)}), 400

    @staticmethod
    def add_comment():
        data = request.json

        # Extraer los datos necesarios del JSON
        id_usuario = data.get('id_usuario')
        id_sitio = data.get('id_sitio')
        opinion = data.get('opinion')

        # Verificar que los IDs de usuario y sitio sean válidos
        if not ObjectId.is_valid(id_usuario) or not ObjectId.is_valid(id_sitio):
            return jsonify({"error": "ID de usuario o sitio no válidos"}), 400

        # Crear una nueva instancia de Review
        review = Review(id_usuario, id_sitio)

        try:
            # Intentar agregar la opinión
            review.add_comment(opinion)
            return jsonify({"mensaje": "Comentario agregado exitosamente"}), 200
        except ValueError as e:
            # Manejar errores en la actualización de la opinión
            return jsonify({"error": str(e)}), 400

    @staticmethod
    def add_qualifi():
        data = request.json

        # Extraer los datos necesarios del JSON
        id_usuario = data.get('id_usuario')
        id_sitio = data.get('id_sitio')
        valor = data.get('valor')

        # Verificar que los IDs de usuario y sitio sean válidos
        if not ObjectId.is_valid(id_usuario) or not ObjectId.is_valid(id_sitio):
            return jsonify({"error": "ID de usuario o sitio no válidos"}), 400

        # Crear una nueva instancia de Review
        new_review = Review(id_usuario, id_sitio)

        try:
            # Intentar agregar la calificación
            new_review.add_qualifi(valor)
            return jsonify({"mensaje": "Calificación agregada exitosamente"}), 201
        except ValueError as e:
            # Manejar errores en la adición de la calificación
            return jsonify({"error": str(e)}), 400
    
# Clase RecomendacionHandler
class RecomendacionHandler:
    @staticmethod
    def reset_cercanos():
        db_manager = MongoDBManager()
        sitio_manager = RecosSitiosManager(db_manager)
        sitio_manager.reset_recos_sitios_collection()
        return jsonify({"mensaje": "Todos los documentos en la colección 'recomendaciones' han sido eliminados y reiniciados"}), 200
    
    @staticmethod
    def add_closest_sites():
        recos_sitio = RecosSitio(MongoDBManager())
        db = MongoDBManager().get_db()
        sitios_collection = db["sitios"]

        try:
            sitios = sitios_collection.find({}, {"_id": 1})
            for sitio in sitios:
                recos_sitio.find_nearest_sites(sitio["_id"])
            return jsonify({"message": "Sitios cercanos y parecidos encontrados y actualizados correctamente"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    @staticmethod
    def buscar_sitios_cercanos():
        db_manager = MongoDBManager()
        recos_sitio = RecosSitio(db_manager)

        data = request.get_json()
        sitio_id = data.get("sitio_id")

        if sitio_id:
            try:
                sitio_id = ObjectId(sitio_id)
                cercanos = recos_sitio.get_sitios_cercanos(sitio_id)
                return jsonify({"sitios_cercanos": cercanos}), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 400
        else:
            return jsonify({"error": "Se requiere proporcionar el ID del sitio"}), 400

    
    @staticmethod
    def buscar_sitios_parecidos():
        db_manager = MongoDBManager()
        recos_sitio = RecosSitio(db_manager)

        sitio_id = request.args.get('sitio_id')
        if sitio_id:
            try:
                sitio_id = ObjectId(sitio_id)
                sitios_parecidos = recos_sitio.get_sitios_parecidos(sitio_id)
                return jsonify({"sitios_parecidos": sitios_parecidos}), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 400
        else:
            return jsonify({"error": "Se requiere proporcionar el ID del sitio"}), 400



api_bp.add_url_rule('/', view_func=lambda: 'Ejecutando API REST')

# Rutas de Usuario
api_bp.add_url_rule('/reset_users', view_func=UserHandler.reset_users, methods=['POST'])
api_bp.add_url_rule('/register', view_func=UserHandler.register, methods=['POST'])
api_bp.add_url_rule('/login', view_func=UserHandler.login, methods=['POST'])
api_bp.add_url_rule('/userinfo', view_func=UserHandler.getinfo, methods=['POST'])

# Rutas de Sitios
api_bp.add_url_rule('/resetsitios', view_func=SitioHandler.reset_sitios, methods=['POST'])
api_bp.add_url_rule('/newsitio', view_func=SitioHandler.new_sitio, methods=['POST'])
api_bp.add_url_rule('/addvisit', view_func=SitioHandler.add_visit, methods=['POST'])

# Rutas de Reviews
api_bp.add_url_rule('/reset_reviews', view_func=ReviewHandler.reset_reviews, methods=['POST'])
api_bp.add_url_rule('/newreview', view_func=ReviewHandler.add_review, methods=['POST'])
api_bp.add_url_rule('/registersitio', view_func=ReviewHandler.register_visit, methods=['POST'])
api_bp.add_url_rule('/addlike', view_func=ReviewHandler.add_like, methods=['POST'])
api_bp.add_url_rule('/addcomment', view_func=ReviewHandler.add_comment, methods=['POST'])
api_bp.add_url_rule('/addqualifi', view_func=ReviewHandler.add_qualifi, methods=['POST'])

# Rutas de Recomendaciones
api_bp.add_url_rule('/reset_cercanos', view_func=RecomendacionHandler.reset_cercanos, methods=['POST'])
api_bp.add_url_rule('/generarsitioscercanos', view_func=RecomendacionHandler.add_closest_sites, methods=['POST'])
api_bp.add_url_rule('/getcercanos', view_func=RecomendacionHandler.buscar_sitios_cercanos, methods=['POST'])
api_bp.add_url_rule('/getparecidos', view_func=RecomendacionHandler.buscar_sitios_parecidos, methods=['POST'])
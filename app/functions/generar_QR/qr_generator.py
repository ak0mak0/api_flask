import os
import qrcode
from app.models import get_db

# Carpeta para guardar los códigos QR
output_dir = os.path.join(os.path.dirname(__file__), 'codigos_QR')

def generate_qr(data, filename):
    # Crear un objeto QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Crear una imagen del QR
    img = qr.make_image(fill='black', back_color='white')

    # Guardar la imagen en un archivo
    img.save(filename)

def generate_qr_for_all_sites():
    # Eliminar archivos existentes en la carpeta de destino
    for filename in os.listdir(output_dir):
        if filename.endswith(".jpg"):
            filepath = os.path.join(output_dir, filename)
            os.remove(filepath)

    db = get_db()
    sitios = db.sitios.find()

    for sitio in sitios:
        sitio_id = str(sitio['_id'])
        nombre_sitio = sitio['nombre_sitio']
        filename = os.path.join(output_dir, f'{nombre_sitio}.jpg')
        generate_qr(sitio_id, filename)

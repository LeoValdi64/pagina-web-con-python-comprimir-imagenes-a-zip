import os
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
import zipfile

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ZIP_FOLDER'] = 'zips/'
app.config['LOW_RES_FOLDER'] = 'img_low/'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'images' not in request.files:
        return jsonify({'error': 'No file part'})

    files = request.files.getlist('images')

    # Procesamiento de imágenes y reducción de resolución
    for i, file in enumerate(files):
        if file.filename == '':
            return jsonify({'error': 'No selected file'})
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Reducir resolución para las primeras 5 imágenes
            if i < 5:
                low_res_path = os.path.join(app.config['LOW_RES_FOLDER'], filename)
                image = Image.open(file_path)
                image.thumbnail((1300, 1300))  # Ajusta las dimensiones según tus necesidades
                # Guardar con calidad reducida al 50%
                image.save(low_res_path, quality=50)

    # Crear archivo ZIP
    zip_filename = "processed_images.zip"
    zip_path = os.path.join(app.config['ZIP_FOLDER'], zip_filename)

    # Crear archivo ZIP y guardarlo en el servidor
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file in files:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            zip_file.write(file_path, filename)

    # Eliminar las imágenes originales después de procesarlas
    for file in files:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))

    
    # Enviar archivo ZIP al cliente
    return jsonify({'success': f'Archivo ZIP guardado en {zip_path} y las imágenes de baja resolución en {app.config["LOW_RES_FOLDER"]}'})


if __name__ == '__main__':
    app.run(debug=True)

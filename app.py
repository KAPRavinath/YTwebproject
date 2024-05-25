from flask import Flask, render_template, request, send_file, session, redirect, url_for
from werkzeug.utils import secure_filename
from reportlab.pdfgen import canvas
from PIL import Image
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this to a strong secret key
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'

# Ensure the upload and output folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    uploaded_files = request.files.getlist('images')
    output_pdf_name = request.form['output_pdf_name']
    image_paths = []

    for file in uploaded_files:
        if file and file.filename:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            image_paths.append(filepath)

    output_pdf_path = os.path.join(app.config['OUTPUT_FOLDER'], output_pdf_name + '.pdf')
    convert_images_to_pdf(image_paths, output_pdf_path)

    session['output_pdf_path'] = output_pdf_path  # Store output path in session
    return redirect(url_for('download'))

@app.route('/download')
def download():
    output_pdf_path = session.get('output_pdf_path')
    if output_pdf_path:
        return render_template('download.html', output_pdf_path=output_pdf_path)
    return redirect(url_for('index'))

@app.route('/download_file')
def download_file():
    output_pdf_path = session.get('output_pdf_path')
    if output_pdf_path:
        return send_file(output_pdf_path, as_attachment=True)
    return redirect(url_for('index'))

def convert_images_to_pdf(image_paths, output_pdf_path):
    pdf = canvas.Canvas(output_pdf_path, pagesize=(612, 792))

    for image_path in image_paths:
        img = Image.open(image_path)
        available_width = 540
        available_height = 720
        scale_factor = min(available_width / img.width, available_height / img.height)
        new_width = img.width * scale_factor
        new_height = img.height * scale_factor
        x_centered = (612 - new_width) / 2
        y_centered = (792 - new_height) / 2

        pdf.setFillColorRGB(1, 1, 1)  # Set fill color to white
        pdf.rect(0, 0, 612, 792, fill=1)
        pdf.drawImage(image_path, x_centered, y_centered, width=new_width, height=new_height)
        pdf.showPage()

    pdf.save()

if __name__ == '__main__':
    app.run(debug=True)
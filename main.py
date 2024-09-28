from flask import Flask, render_template, request, url_for, redirect
import os
import PyPDF2
import requests
import io
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Set the folder where PDFs are stored
PDF_FOLDER = 'pdf_files'
app.config['UPLOAD_FOLDER'] = PDF_FOLDER

# Ensure the PDF folder exists
os.makedirs(PDF_FOLDER, exist_ok=True)

pdf_storage = {}

def process_pdf(file_path, from_url=False):
    if from_url:
        response = requests.get(file_path)
        pdf_file = io.BytesIO(response.content)
    else:
        pdf_file = open(file_path, 'rb')

    with pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        num_pages = len(pdf_reader.pages)
        num_images = sum(1 for page in pdf_reader.pages for image in page.images)
        num_audio = 0  # PyPDF2 doesn't have built-in audio detection
        num_video = 0  # PyPDF2 doesn't have built-in video detection

    return {
        'filename': os.path.basename(file_path),
        'pages': num_pages,
        'images': num_images,
        'audio': num_audio,
        'video': num_video
    }

def scan_pdf_folder():
    for filename in os.listdir(PDF_FOLDER):
        if filename.lower().endswith('.pdf') and filename not in pdf_storage:
            file_path = os.path.join(PDF_FOLDER, filename)
            try:
                pdf_stats = process_pdf(file_path)
                pdf_storage[filename] = pdf_stats
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

@app.route('/', methods=['GET', 'POST'])
def index():
    error_message = None
    if request.method == 'POST':
        submitted_url = request.form['url']
        if submitted_url.lower().endswith('.pdf'):
            try:
                pdf_stats = process_pdf(submitted_url, from_url=True)
                filename = secure_filename(os.path.basename(submitted_url))
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                # Download and save the PDF
                response = requests.get(submitted_url)
                with open(file_path, 'wb') as f:
                    f.write(response.content)

                pdf_storage[filename] = pdf_stats
            except Exception as e:
                error_message = f"Error processing PDF: {str(e)}"
        else:
            error_message = "The submitted URL does not point to a PDF file."

    scan_pdf_folder()  # Scan the folder each time the page is loaded
    pdf_files = list(pdf_storage.values())
    return render_template('pdf_list.html', pdf_files=pdf_files, error_message=error_message)

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template, request, url_for
import os
from pdf_processor import PDFProcessor

app = Flask(__name__)

# Set the folder where PDFs are stored
PDF_FOLDER = 'pdf_files'
app.config['UPLOAD_FOLDER'] = PDF_FOLDER

# Ensure the PDF folder exists
os.makedirs(PDF_FOLDER, exist_ok=True)

# Initialize PDFProcessor
pdf_processor = PDFProcessor(PDF_FOLDER)


@app.route('/', methods=['GET', 'POST'])
def index():
    error_message = None
    if request.method == 'POST':
        submitted_url = request.form['url']
        error_message = pdf_processor.process_url(submitted_url)

    pdf_processor.scan_pdf_folder(
    )  # Scan the folder each time the page is loaded
    pdf_files = pdf_processor.get_pdf_files()
    return render_template('pdf_list.html',
                           pdf_files=pdf_files,
                           error_message=error_message)


if __name__ == '__main__':
    app.run(debug=True)

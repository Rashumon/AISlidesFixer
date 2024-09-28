import os
import PyPDF2
import requests
import io
from werkzeug.utils import secure_filename

class PDFProcessor:
    def __init__(self, pdf_folder):
        self.pdf_folder = pdf_folder
        self.pdf_storage = {}

    def process_pdf(self, file_path, from_url=False):
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

    def scan_pdf_folder(self):
        for filename in os.listdir(self.pdf_folder):
            if filename.lower().endswith('.pdf') and filename not in self.pdf_storage:
                file_path = os.path.join(self.pdf_folder, filename)
                try:
                    pdf_stats = self.process_pdf(file_path)
                    self.pdf_storage[filename] = pdf_stats
                except Exception as e:
                    print(f"Error processing {filename}: {str(e)}")

    def process_url(self, url):
        if url.lower().endswith('.pdf'):
            try:
                pdf_stats = self.process_pdf(url, from_url=True)
                filename = secure_filename(os.path.basename(url))
                file_path = os.path.join(self.pdf_folder, filename)

                # Download and save the PDF
                response = requests.get(url)
                with open(file_path, 'wb') as f:
                    f.write(response.content)

                self.pdf_storage[filename] = pdf_stats
                return None  # No error
            except Exception as e:
                return f"Error processing PDF: {str(e)}"
        else:
            return "The submitted URL does not point to a PDF file."

    def get_pdf_files(self):
        return list(self.pdf_storage.values())
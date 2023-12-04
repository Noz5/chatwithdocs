from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)
from flask import Flask, render_template, request
import pdfplumber
from docx import Document
import os

app = Flask(__name__)

OPENAI_API_KEY = "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"

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def analyze_document(document_text):
    

    response = client.completions.create(model="gpt-3-turbo",
    prompt="Analyze and summarize the following text:\n" + document_text,
    temperature=0.7,
    max_tokens=1000)

    analysis_text = response["choices"][0]["text"]
    return analysis_text

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the posted file is valid
        if request.files['file'] and allowed_file(request.files['file'].filename):
            filename = request.files['file'].filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Save the file to the uploads folder
            request.files['file'].save(file_path)

            # Extract text from the uploaded document
            if file_path.endswith('.pdf'):
                with open(file_path, 'rb') as f:
                    pdf = pdfplumber.open(f)
                    pages = pdf.pages
                    document_text = '\n'.join([page.extract_text() for page in pages])
            elif file_path.endswith('.docx'):
                with open(file_path, 'rb') as f:
                    doc = Document(f)
                    paragraphs = doc.paragraphs
                    document_text = '\n'.join([paragraph.text for paragraph in paragraphs])

            # Analyze the document using the OpenAI API
            analysis_text = analyze_document(document_text)

            # Display the analysis text
            return render_template('analysis.html', analysis_text=analysis_text)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

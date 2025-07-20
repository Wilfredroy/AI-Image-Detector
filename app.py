from flask import Flask, render_template, request, jsonify
import requests
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Sightengine API details
API_URL = "https://api.sightengine.com/1.0/check.json"
API_USER = "842246742"
API_SECRET = "ZumKZby4rQDaYSYPgijNmqoZmUdRwrkF"

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    image = request.files['image']
    if image.filename == '' or not allowed_file(image.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    filename = secure_filename(image.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(filepath)
    
    files = {'media': open(filepath, 'rb')}
    params = {
        'models': 'genai',
        'api_user': API_USER,
        'api_secret': API_SECRET
    }
    
    response = requests.post(API_URL, files=files, data=params)
    
    if response.status_code == 200:
        result = response.json()
        ai_score = result.get("type", {}).get("ai_generated", 0)
        
        if ai_score > 0.5:
            final_result = "AI Generated"
        else:
            final_result = "Not AI Generated"
        
        return jsonify({'result': final_result})
    else:
        return jsonify({'error': 'Failed to analyze image'}), response.status_code

if __name__ == '__main__':
    app.run(debug=True)

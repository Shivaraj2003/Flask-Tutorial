from flask import Blueprint, render_template, request, redirect, url_for, flash
from Main.models import insert_user, get_all_users, User
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Import the ML model function
from Main.ml_model import transcribe_audio

app_routes = Blueprint('app_routes', __name__)

@app_routes.route('/')
def index():
    return render_template('index.html')

@app_routes.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Insert user into the database
        insert_user(username, email, password)
        return redirect(url_for('app_routes.upload_file'))

    return render_template('signup.html')

@app_routes.route('/view_db')
def view_db():
    users = get_all_users()
    return render_template('success.html', users=users)

@app_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Fetch user from the database
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:  # Compare passwords
            # Valid credentials
            return redirect(url_for('app_routes.upload_file'))
        else:
            # Invalid credentials
            flash('Invalid username or password', 'error')
            return render_template('login.html')  # Re-render login page with error

    return render_template('login.html')

@app_routes.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        # Check if the file is allowed
        if file and allowed_file(file.filename):
            # Secure the filename to prevent issues with special characters
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            # Save the file to the 'uploads' folder
            file.save(filepath)
            
            # Process the file (e.g., transcribe it)
            transcription = transcribe_audio(filepath)
            
            # Redirect to the result page with transcription as a URL parameter
            # return redirect(url_for('app_routes.transcription_result', transcription=transcription))
            return render_template('speech_to_text.html', transcription=transcription)
        else:
            return jsonify({"error": "Invalid file format"}), 400

    return render_template('upload.html')



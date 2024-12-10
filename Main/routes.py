from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from Main.models import insert_user, get_all_users, User, Transcription, insert_transcription, get_all_records, Report, insert_report, get_all_reports
from werkzeug.utils import secure_filename
import os
import requests  # To send the file to Colab via HTTP
from dotenv import load_dotenv
from Main import db

# Load environment variables from .env file
load_dotenv()

# Fetch the Ngrok public URL from environment variables
NGROK_PUBLIC_URL = os.getenv('NGROK_PUBLIC_URL')  # Ensure to define this in your .env

# Configure file upload settings
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac'}

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Blueprint for app routes
app_routes = Blueprint('app_routes', __name__)

@app_routes.route('/')
def index():
    return render_template('EditedHomePage.html')

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
    return render_template('users.html', users = users)

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
            
            # Send the file to Colab for transcription
            transcription = send_to_colab(filepath)
            # transcription = "Good job "
            print(transcription)
            if transcription:
                #insert_report(filename, transcription)
                report = transcription[0]
                insert_report(report['Name'],report['Age'],report['Symptoms'],report['Diagnosis'], report['Treatment'],filename)
                return render_template('speech_to_text.html', transcription=transcription[0])
            else:
                return jsonify({"error": "Failed to process the file on Colab"}), 500

        else:
            return jsonify({"error": "Invalid file format"}), 400

    return render_template('upload.html')



@app_routes.route('/check-unique', methods=['POST'])
def check_unique():
    """Checks if a username or email is unique."""
    username = request.json.get('username', None)
    email = request.json.get('email', None)

    if username:
        user = User.query.filter_by(username=username).first()
        if user:
            return jsonify({"username_exists": True, "field": "username"})
    if email:
        user = User.query.filter_by(email=email).first()
        if user:
            return jsonify({"email_exists": True, "field": "email"})

    return jsonify({"email_exists":False, "user_exists":True})
                    
def send_to_colab(filepath):
    if not NGROK_PUBLIC_URL:
        print("Error: Ngrok public URL is not set.")
        return None

    url = f"{NGROK_PUBLIC_URL}/process_audio"  # Assuming you have a /transcribe endpoint in your Colab Flask app

    with open(filepath, 'rb') as audio_file:
        files = {'file': audio_file}
        try:
            # Send the file to Colab for transcription
            response = requests.post(url, files=files)
            
            # Check the response status code
            if response.status_code == 200:
                # Extract the transcription from the response
                transcription = response.json()
                
                return transcription
            else:
                print(f"Error: {response.status_code}, {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Request Exception occurred: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error occurred: {e}")
            return None


@app_routes.route('/delete_patient/<int:report_id>', methods=['POST'])
def delete_patient(report_id):
    patient =  Report.query.get(report_id)

    if not patient:
        return 'Page Not Found', 404
    
    db.session.delete(patient)
    db.session.commit() 
    return redirect(url_for('app_routes.view_reports'))

@app_routes.route('/view_reports')
def view_reports():
    reports = get_all_reports()
    return render_template('report.html', reports=reports)
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from Main.models import insert_user, get_all_users, User, Transcription, insert_transcription, get_all_records, Report, insert_report, get_all_reports
from werkzeug.utils import secure_filename
from functools import wraps
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

# Secret key for session management (configure in .env for production)
app_secret_key = os.getenv('SECRET_KEY', 'your_default_secret_key')

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:  # Check if the user is logged in
            session['next_url'] = request.url  # Save the current URL to return after login
            session['alert_message'] = "Please login to continue"  # Store alert message in session
            return redirect(url_for('app_routes.login'))  # Redirect to login page
        
        return f(*args, **kwargs)
    return decorated_function

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
        flash('Signup successful! Please log in.', 'success')
        return redirect(url_for('app_routes.login'))

    return render_template('signup.html')

@app_routes.route('/view_db')
@login_required
def view_db():
    users = get_all_users()
    return render_template('users.html', users=users)

@app_routes.route('/login', methods=['GET', 'POST'])
def login():
    alert_message = session.pop('alert_message', None)  # Get the alert message if it exists

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Fetch user from the database
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:  # Compare passwords
            # Store user in session
            session['user_id'] = user.id
            session['username'] = user.username

            # Redirect to the saved next URL or default to the upload page
            next_url = session.pop('next_url', url_for('app_routes.upload_file'))
            return redirect(next_url)

        else:
            alert_message = "Invalid username or password"  # Set alert message for login failure

    return render_template('login.html', alert_message=alert_message)



@app_routes.route('/logout')
def logout():
    session.clear()  # Clear all session data
    flash('You have been logged out.', 'info')
    return redirect(url_for('app_routes.login'))

@app_routes.route('/upload', methods=['GET', 'POST'])
@login_required
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
            print(transcription)
            if transcription:
                report = transcription[0]
                insert_report(report['Name'], report['Age'], report['Symptoms'], report['Diagnosis'], report['Treatment'], filename)
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

    return jsonify({"email_exists": False, "user_exists": True})

def send_to_colab(filepath):
    if not NGROK_PUBLIC_URL:
        print("Error: Ngrok public URL is not set.")
        return None

    url = f"{NGROK_PUBLIC_URL}/process_audio"

    with open(filepath, 'rb') as audio_file:
        files = {'file': audio_file}
        try:
            response = requests.post(url, files=files)
            if response.status_code == 200:
                transcription = response.json()
                return transcription
            else:
                print(f"Error: {response.status_code}, {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Request Exception occurred: {e}")
            return None

@app_routes.route('/delete_patient/<int:report_id>', methods=['POST'])
@login_required
def delete_patient(report_id):
    patient = Report.query.get(report_id)

    if not patient:
        return 'Page Not Found', 404

    db.session.delete(patient)
    db.session.commit()
    return redirect(url_for('app_routes.view_reports'))

@app_routes.route('/view_reports')
@login_required
def view_reports():
    reports = get_all_reports()
    return render_template('report.html', reports=reports)

# Import necessary libraries
from flask import Flask, request, jsonify
from pyngrok import ngrok
from werkzeug.utils import secure_filename
import os
import whisper

# Initialize Flask app
app = Flask(__name__)

# Set Ngrok auth token (replace with your own Ngrok auth token)
ngrok.set_auth_token("your_code")  # RCheck in .env

# Configure file upload settings
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac'}

# Function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Load the Whisper model
model = whisper.load_model("small")  # You can change 'large' to 'small', 'medium', etc.

# Function to transcribe audio using Whisper
def transcribe_audio(filepath):
    result = model.transcribe(filepath)
    return result['text']

# Define routes

@app.route('/', methods=["GET"])
def home():
    return jsonify({"message": "Welcome to the Flask app in Colab!"})

@app.route('/transcribe', methods=["POST"])
def transcribe_file():
    # Check if 'file' is in the request
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        # Secure the filename and save the file locally
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Transcribe the audio using Whisper
        transcription = transcribe_audio(filepath)

        # Return the transcription as JSON
        return jsonify({"transcription": transcription})

    return jsonify({"error": "Invalid file format"}), 400

# Start Flask app with Ngrok tunneling
def start_app():
    # Start Ngrok tunnel to expose the app to the public internet
    public_url = ngrok.connect(5000)
    print(f"Ngrok Public URL: {public_url}")

    # Start the Flask app
    app.run(port=5000, use_reloader=False)  # use_reloader=False to prevent restart issues in Colab

# Run the app
start_app()

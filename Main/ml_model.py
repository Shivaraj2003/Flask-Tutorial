# import speech_recognition as sr
# import os
# from pydub import AudioSegment
# import noisereduce as nr
# import librosa
# import soundfile as sf  # Import the soundfile library

# # Path for uploading files 
# UPLOAD_FOLDER = './uploads'


# # Function to preprocess audio (convert to WAV, reduce noise, etc.)
# def preprocess_audio(file_path):
#     # Noise reduction using noisereduce and librosa
#     audio, sr = librosa.load(file_path, sr=None)
#     audio = nr.reduce_noise(y=audio, sr=sr)

#     # Save the preprocessed audio file using soundfile
#     preprocessed_file_path = os.path.join(UPLOAD_FOLDER, 'preprocessed_' + os.path.basename(file_path))
#     sf.write(preprocessed_file_path, audio, sr)
    
#     return preprocessed_file_path


# # Function to convert audio file to text using speech recognition
# def transcribe_audio(file_path):
#     recognizer = sr.Recognizer()

#     # Preprocess the audio file (if necessary)
#     preprocessed_file = preprocess_audio(file_path)

#     # Open the preprocessed audio file
#     with sr.AudioFile(preprocessed_file) as source:
#         audio = recognizer.record(source)  # Record the audio

#     try:
#         # Recognize speech using Google Web Speech API
#         text = recognizer.recognize_google(audio)
#         return text
#     except sr.UnknownValueError:
#         return "Google Speech Recognition could not understand the audio"
#     except sr.RequestError:
#         return "Could not request results from Google Speech Recognition service"


# # Example of using the function (in your application flow)
# # def process_audio(file_path):
# #     # Transcribe audio after preprocessing
# #     transcription = transcribe_audio(file_path)
    
# #     # Post-processing (optional)
# #     # Here you could implement more advanced post-processing (e.g., spell check, punctuation restoration)
    
# #     return transcription


# # import speech_recognition as sr

# # # Function to convert audio file to text
# # def transcribe_audio(file_path):
# #     recognizer = sr.Recognizer()

# #     # Open the audio file
# #     with sr.AudioFile(file_path) as source:
# #         audio = recognizer.record(source)  # Record the audio

# #     try:
# #         # Recognize speech using Google Web Speech API
# #         text = recognizer.recognize_google(audio)
# #         return text
# #     except sr.UnknownValueError:
# #         return "Google Speech Recognition could not understand the audio"
# #     except sr.RequestError:
# #         return "Could not request results from Google Speech Recognition service"
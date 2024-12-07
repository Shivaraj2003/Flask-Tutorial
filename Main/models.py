from Main import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

def insert_user(username, email, password):
    user = User(username=username, email=email, password=password)
    db.session.add(user)
    db.session.commit()

def get_all_users():
    return User.query.all()


class Transcription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    transcription = db.Column(db.String(255), nullable=False)
    

def insert_transcription(filename, transcription):
    record = Transcription(filename = filename, transcription = transcription)
    db.session.add(record)
    db.session.commit()

def get_all_records():
    return Transcription.query.all()


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.String(10), nullable=False)
    symptoms = db.Column(db.Text, nullable=False)
    diagnosis = db.Column(db.Text, nullable=False)
    treatment = db.Column(db.Text, nullable=False)
    audio_file = db.Column(db.String(200), nullable=True)

def insert_report(name, age, symptoms, diagnosis, treatment, audio_file=None):
    report = Report(
        name=name,
        age=age,
        symptoms=symptoms,
        diagnosis=diagnosis,
        treatment=treatment,
        audio_file=audio_file
    )
    db.session.add(report)
    db.session.commit()

def get_all_reports():
    return Report.query.all()

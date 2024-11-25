from flask import Blueprint, render_template, request, redirect, url_for, flash
from Main.models import insert_user, get_all_users, User

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
        return redirect(url_for('app_routes.view_db'))

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
            users = get_all_users()
            return render_template('success.html', users = users)
        else:
            # Invalid credentials
            flash('Invalid username or password', 'error')
            return render_template('login.html')  # Re-render login page with error

    return render_template('login.html')  # GET request renders login page

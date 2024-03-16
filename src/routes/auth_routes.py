from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from src.database.db import get_db, SessionLocal
from src.models.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/is_authenticated")
def is_authenticated():
    return jsonify({"authenticated": current_user.is_authenticated})


@auth_bp.route("/current_user")
def get_current_user():
    return jsonify({"current_user": current_user})


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        db = get_db()
        user = User(username=username, email=email)
        user.set_password(password)
        db.add(user)
        db.commit()
        db.close()
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        user = db.query(User).filter(User.username == username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('predict.upload_predict'))
        else:
            flash('Invalid username or password')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

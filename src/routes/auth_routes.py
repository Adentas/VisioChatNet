from datetime import datetime

from sqlalchemy.orm.exc import NoResultFound

from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from src.database.db import get_db, SessionLocal
from src.models.models import User
from src.utils.decorators import logout_required
from src.utils.token import confirm_token, generate_token
from src.utils.email import send_email

auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/is_authenticated")
def is_authenticated():
    return jsonify({"authenticated": current_user.is_authenticated})


@auth_bp.route("/current_user")
def get_current_user():
    return jsonify({"current_user": current_user})


@auth_bp.route('/register', methods=['GET', 'POST'])
@logout_required
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if len(password) < 6:
            flash('Your password must be at least 6 characters long.', 'error')
            return render_template('auth/register.html')

        db = SessionLocal()
        user_exists = False

        try:
            user = db.query(User).filter((User.username == username) | (User.email == email)).one()
            user_exists = True
        except NoResultFound:
            user_exists = False

        if user_exists:
            flash('A user with this username or email already exists.', 'error')
            db.close()
            return render_template('auth/register.html')

        user = User(username=username, email=email)
        user.set_password(password)
        db.add(user)
        db.commit()
        token = generate_token(user.email)
        confirm_url = url_for("auth.confirm_email", token=token, _external=True)
        html = render_template("auth/confirm_email.html", confirm_url=confirm_url)
        subject = "Please confirm your email"
        send_email(user.email, subject, html)

        login_user(user)
        db.close()
        flash("A confirmation email has been sent via email.", "success")
        # return redirect(url_for("auth.inactive"))
        return render_template('auth/login.html')

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
@logout_required
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = SessionLocal()
        user = db.query(User).filter(User.username == username).first()

        if user is None:
            flash('No user found with that username.', 'error')
            db.close()
            return render_template('auth/login.html')

        if not check_password_hash(user.password_hash, password):
            flash('Invalid password.', 'error')
            db.close()
            return render_template('auth/login.html')

        login_user(user)
        db.close()
        return redirect(url_for('predict.upload_predict'))

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.route("/confirm/<token>")
@login_required
def confirm_email(token):
    if current_user.is_confirmed:
        flash("Account already confirmed.", "success")
        return redirect(url_for("home"))
    email = confirm_token(token)
    db = SessionLocal()
    user = db.query(User).filter_by(email=current_user.email).first()
    if user.email == email:
        user.is_confirmed = True
        user.confirmed_on = datetime.now()
        db.add(user)
        db.commit()
        flash("You have confirmed your account. Thanks!", "success")
    else:
        flash("The confirmation link is invalid or has expired.", "danger")
    db.close()
    # return redirect(url_for("home"))
    return render_template('auth/login.html')


# @auth_bp.route("/inactive")
# @login_required
# def inactive():
#     if current_user.is_confirmed:
#         return redirect(url_for("home"))
#     return render_template("auth/inactive.html")


@auth_bp.route("/resend")
@login_required
def resend_confirmation():
    if current_user.is_confirmed:
        flash("Your account has already been confirmed.", "success")
        return redirect(url_for("home"))
    token = generate_token(current_user.email)
    confirm_url = url_for("auth.confirm_email", token=token, _external=True)
    html = render_template("auth/confirm_email.html", confirm_url=confirm_url)
    subject = "Please confirm your email"
    send_email(current_user.email, subject, html)
    flash("A new confirmation email has been sent.", "success")
    return redirect(url_for("auth.login"))

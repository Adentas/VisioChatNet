from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user


def logout_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            flash("You are already authenticated.", "info")
            return redirect(url_for("home"))
        return func(*args, **kwargs)

    return decorated_function


def check_is_confirmed(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_confirmed is False:
            flash("Please confirm your account!", "warning")
            return redirect(url_for("auth.inactive"))
        return func(*args, **kwargs)

    return decorated_function

import os

from sqlalchemy import text
from src.database.db import SessionLocal
from src.routes.auth_routes import auth_bp
from src.models.models import User
from src.routes.predict_routes import predict_bp
from src.routes.history_routes import history_bp
from src.utils.decorators import check_is_confirmed
from src.utils.cache_config import cache
from src import app

from flask import Flask, jsonify, render_template
from flask_login import LoginManager, current_user

app.secret_key = os.getenv("SECRET_KEY")
cache.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = "auth.login"
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(history_bp, url_prefix="/history")
app.register_blueprint(predict_bp, url_prefix='/predict')


@login_manager.user_loader
def load_user(user_id):
    db = SessionLocal()
    return db.query(User).get(int(user_id))


@app.route("/")
@cache.cached(timeout=300, key_prefix='home_page')
def home():
    return render_template("home/home.html")


@app.route("/healthchecker")
def healthchecker():
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT 1")).fetchone()
        db.close()
        if result is None:
            return jsonify({"detail": "Database is not configured correctly"}), 500
        return jsonify({"message": "Welcome to Flask! Database connected correctly"})
    except Exception as e:
        return jsonify({"detail": f"Error connecting to the database: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5001)

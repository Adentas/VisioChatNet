from itsdangerous import URLSafeTimedSerializer

from src.conf.config import settings


def generate_token(email):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    return serializer.dumps(email, salt=settings.SECURITY_PASSWORD_SALT)


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    try:
        email = serializer.loads(
            token, salt=settings.SECURITY_PASSWORD_SALT, max_age=expiration
        )
        return email
    except Exception:
        return False
"""
Authentification GUELANE — hachage de mots de passe + tokens JWT.

- Les mots de passe ne sont JAMAIS stockés en clair : on stocke un hachage bcrypt.
- La connexion renvoie un token JWT que le navigateur garde et envoie à chaque requête.
"""
import os
from datetime import datetime, timedelta
import bcrypt
from jose import jwt, JWTError

# Clé secrète pour signer les tokens. En prod, définir PROPHET_SECRET_KEY dans .env.
SECRET_KEY = os.environ.get("PROPHET_SECRET_KEY", "dev-secret-change-me-in-production")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24 * 7  # 7 jours


def _to_bytes(password: str) -> bytes:
    # bcrypt limite à 72 octets — on tronque proprement.
    return password.encode("utf-8")[:72]


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(_to_bytes(password), salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(_to_bytes(plain), hashed.encode("utf-8"))
    except Exception:
        return False


def create_token(email: str) -> str:
    """Crée un token JWT valide 7 jours pour cet email."""
    expire = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    payload = {"sub": email, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> str | None:
    """Renvoie l'email si le token est valide, sinon None."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None

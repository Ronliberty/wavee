# yourapp/utils/invite_jwt.py
import jwt
import uuid
from datetime import datetime, timedelta, timezone
from django.conf import settings

INVITE_SECRET = getattr(settings, "INVITE_JWT_SECRET", settings.SECRET_KEY)
INVITE_ALGO = getattr(settings, "INVITE_JWT_ALGORITHM", "HS256")
DEFAULT_EXP_HOURS = getattr(settings, "INVITE_DEFAULT_EXPIRY_HOURS", 24)
ISSUER = getattr(settings, "INVITE_JWT_ISSUER", "users")

def create_invite_jwt(email=None, role="user", expiry_hours=None, extra_claims=None):
    """Return a signed JWT string for invite."""
    expiry_hours = expiry_hours or DEFAULT_EXP_HOURS
    jti = str(uuid.uuid4())
    now = datetime.now(tz=timezone.utc)
    exp = now + timedelta(hours=expiry_hours)
    payload = {
        "jti": jti,
        "iss": ISSUER,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "role": role,
    }
    if email:
        payload["email"] = email
    if extra_claims:
        payload.update(extra_claims)
    token = jwt.encode(payload, INVITE_SECRET, algorithm=INVITE_ALGO)
    # PyJWT returns str in v2
    return token

def decode_invite_jwt(token, verify_expiry=True):
    """Decode and verify token. Raises jwt exceptions on failure."""
    options = {"verify_exp": verify_expiry}
    payload = jwt.decode(token, INVITE_SECRET, algorithms=[INVITE_ALGO], options=options)
    return payload

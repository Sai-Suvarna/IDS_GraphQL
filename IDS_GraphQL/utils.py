import jwt
import Authentication.models  
from datetime import datetime
from graphql_jwt.settings import jwt_settings

## JWT payload 
def jwt_payload(user, context=None):
    """
    Generates a JWT payload 

    Args:
    - user: User object representing the authenticated user.
    - context: Optional context data (not used in this function).

    Returns:
    - payload: Dictionary containing JWT payload data.
    """
    # Calculate JWT expiration datetime
    jwt_datetime = datetime.utcnow() + jwt_settings.JWT_EXPIRATION_DELTA
    jwt_expires = int(jwt_datetime.timestamp())

    # Build JWT payload
    payload = {}
    payload['username'] = str(user.username)  # For library compatibility
    payload['id'] = str(user.userId)  # Subject identifier (user ID)
    payload['sub_name'] = user.username  # Subject name (username)
    payload['sub_email'] = user.email  # Subject email
    payload['exp'] = jwt_expires  # JWT expiration timestamp

    return payload


import jwt
from django.conf import settings

def get_username_from_token(token):
    try:
        # Decode the token
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        return decoded.get("username")
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")

from src.error import AccessError
from src.data_store import data_store
import hashlib
import jwt

SESSION_TRACKER = 0
SECRET = 'COMP1531'

def generate_new_session_id():
    """Generates a new sequential session ID

    Returns:
        number: The next session ID
    """
    global SESSION_TRACKER
    SESSION_TRACKER += 1
    return SESSION_TRACKER


def hash(input_string):
    """Hashes the input string with sha256

    Args:
        input_string ([string]): The input string to hash

    Returns:
        string: The hexidigest of the encoded string
    """
    return hashlib.sha256(input_string.encode()).hexdigest()


def generate_jwt(user_id, session_id=None):
    """Generates a JWT using the global SECRET

    Args:
        username ([string]): The username
        session_id ([string], optional): The session id, if none is provided will
                                         generate a new one. Defaults to None.

    Returns:
        string: A JWT encoded string
    """
    if session_id is None:
        session_id = generate_new_session_id()
    return jwt.encode({'user_id': user_id, 'session_id': session_id}, SECRET, algorithm='HS256')


def decode_jwt(encoded_jwt):
    """Decodes a JWT string into an object of the data

    Args:
        encoded_jwt ([string]): The encoded JWT as a string

    Returns:
        Object: An object storing the body of the JWT encoded string
    """
    return jwt.decode(encoded_jwt, SECRET, algorithms=['HS256'])


def validate_token(encoded_jwt):
    user_id_list = filter_data_store(list='users', key='is_removed', value=False)
    user_id_list = [user['id'] for user in user_id_list]
    try:
        decoded_jwt = decode_jwt(encoded_jwt)
    except Exception:
        decoded_jwt = None

    ### Not sure if we need to check if valid auth_user_id is passed ###
    if decoded_jwt is None or decoded_jwt['user_id'] not in user_id_list:
        raise AccessError(description='Invalid Token')
    else:
        session_id_list = filter_data_store(list='users', key='id', value=decoded_jwt['user_id'])
        if decoded_jwt['session_id'] not in session_id_list:
            raise AccessError(description='Invalid Token')
    
    return decoded_jwt
    #return decoded_jwt['user_id']


# Used to replace list comprehensions when filtering the data store
def filter_data_store(list, key=None, value=None):
    store = data_store.get()

    if value is not None and key is not None:
        filtered_list = [item for item in store[list] if item[key] == value]
        if len(filtered_list) == 0:
            return None
        return filtered_list[0]
        
    elif key is not None:
        return [item[key] for item in store[list]]

    return [item for item in store[list]]

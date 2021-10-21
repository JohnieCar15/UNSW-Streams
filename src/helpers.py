import jwt
from src.error import AccessError
from src.data_store import data_store

SESSION_TRACKER = 0
SECRET = 'JOjQqnzcMKrLVsTVLNc2hzA4iWkqqcQB'

def generate_new_session_id():
    global SESSION_TRACKER
    SESSION_TRACKER += 1
    return SESSION_TRACKER

def generate_jwt(user_id, session_id=None):
    if session_id is None:
        session_id = generate_new_session_id()
    return jwt.encode({'user_id': user_id, 'session_id': session_id}, SECRET, algorithm='HS256')


def decode_jwt(encoded_jwt):
    return jwt.decode(encoded_jwt, SECRET, algorithms='HS256')
    

def validate_token(encoded_jwt):
    user_id_list = filter_data_store(store='users', key='id')
    try:
        decoded_jwt = decode_jwt(encoded_jwt)
    except Exception:
        decoded_jwt = None

    ### Not sure if we need to check if valid auth_user_id is passed ###
    if decoded_jwt is None or decoded_jwt['user_id'] not in user_id_list:
        raise AccessError(description='Invalid Token')
    else:
        session_id_list = filter_data_store(store='users', key='id', value=decoded_jwt['user_id'])
        if decoded_jwt['session_id'] not in session_id_list[0]['session_list']:
            raise AccessError(description='Invalid Token')
    
    return decoded_jwt
    #return decoded_jwt['user_id']

# Used to replace list comprehensions when filtering the data store
def filter_data_store(store, key=None, value=None):
    store = data_store.get()
    if value is not None and key is not None:
        filtered_list = [item for item in store[store] if (isinstance(item[key], list) and value in item[key]) or item[key] == value]
        if len(filtered_list) == 0:
            return None
        return filtered_list
        
    elif key is not None:
        return [item[key] for item in store[store]]
    return [item for item in store[store]]

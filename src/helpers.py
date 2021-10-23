import jwt
from src.error import AccessError
from src.data_store import data_store

session_tracker = 0
SECRET = 'JOjQqnzcMKrLVsTVLNc2hzA4iWkqqcQB'

def generate_new_session_id():
    global session_tracker
    session_tracker += 1
    return session_tracker

def generate_jwt(user_id, session_id):
    return jwt.encode({'user_id': user_id, 'session_id': session_id}, SECRET, algorithm='HS256')


def decode_jwt(encoded_jwt):
    return jwt.decode(encoded_jwt, SECRET, algorithms='HS256')
    

def validate_token(encoded_jwt):
    user_id_list = filter_data_store(store_list='users', key='id')
    try:
        decoded_jwt = decode_jwt(encoded_jwt)
    except Exception:
        decoded_jwt = None

    if decoded_jwt is None or decoded_jwt['user_id'] not in user_id_list:
        raise AccessError(description='Invalid Token')
    else:
        session_id_list = filter_data_store(store_list='users', key='id', value=decoded_jwt['user_id'])
        if decoded_jwt['session_id'] not in session_id_list[0]['session_list']:
            raise AccessError(description='Invalid Token')
    
    return decoded_jwt

# Used to replace list comprehensions when filtering the data store
def filter_data_store(store_list, key, value=None):
    store = data_store.get()
    if value is not None:
        return [item for item in store[store_list] if (isinstance(item[key], list) and value in item[key]) or item[key] == value]
    
    return [item[key] for item in store[store_list]]

# For a given user_id, checks to see if the user is a global owner
def is_global_owner(u_id):
    user_dict = filter_data_store(store_list='users', key='id',value=u_id)
    return user_dict[0]['permission_id'] == 1

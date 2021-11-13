import jwt
from datetime import datetime, timezone
from src.error import AccessError
from src.data_store import data_store, session_tracker, SECRET, img_tracker


def generate_new_session_id():
    '''
    generate_new_session_id: Creates a new session_id when logging in or registering
    '''
    global session_tracker
    session_tracker += 1
    return session_tracker

def generate_new_img_id():
    '''
    generate_new_img_id: Creates a new img_id when uploading a new profile photo
    '''
    global img_tracker
    img_tracker += 1
    return img_tracker

def generate_jwt(user_id, session_id):
    '''
    generate_jwt: Creates a jwt storing the user_id and session_id
    '''
    return jwt.encode({'user_id': user_id, 'session_id': session_id}, SECRET, algorithm='HS256')


def decode_jwt(encoded_jwt):
    '''
    decode_jwt: Decodes a jwt storing the user_id and session_id
    '''
    return jwt.decode(encoded_jwt, SECRET, algorithms='HS256')
    

def validate_token(encoded_jwt):
    '''
    validate_token: Validates the token to see if the data has been tampered with
    '''
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
    
    update_user_status(decoded_jwt['user_id'])
    return decoded_jwt


def filter_data_store(store_list, key, value=None):
    '''
    filter_data_store: Filters the data_store to return the specified key and value
    '''
    store = data_store.get()
    if value is not None:
        return [item for item in store[store_list] if (isinstance(item[key], list) and value in item[key]) or item[key] == value]
    
    return [item[key] for item in store[store_list]]


def is_global_owner(u_id):
    '''
    is_global_owner: For a given user_id, checks to see if the user is a global owner
    '''
    user_dict = filter_data_store(store_list='users', key='id',value=u_id)
    return user_dict[0]['permission_id'] == 1

def update_user_status(user_id):
    '''
    update_user_status: update timestamp for user's last opration,
    if the latest user_status is 'away', srt it to 'available'
    
    This dunction will be called in validate_token(encoded_jwt), since all functions calls validate_token(encoded_jwt)
    Exceptions: the five function below don't call validate_token(encoded_jwt)
        auth_register_v2 and auth_login_v2
               * for these two the update of timestamp is in another way
        auth_passwordreset_request_v1 and auth_passwordreset_reset_v1 
               * no need to update timestamp since the use have not actually login yet
        clear_v1
               * no need to update timestamp
    '''
    user = filter_data_store(store_list='users', key='id', value=user_id)[0]
    user['last_opration_time_stamp'] = int(datetime.now(timezone.utc).timestamp())
    # if the latest user_status is 'away', srt it to 'available'
    user['user_status'] = 'available' if user['user_status'] == 'away' else user['user_status']

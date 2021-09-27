from src.data_store import data_store
from src.error import InputError

def auth_login_v1(email, password):
    store = data_store.get()

    for user in store['users']:
        if user[1] == email:
            if user[2] == password:
                return {
                    'auth_user_id': auth_user_id,
                }
            else:
                raise InputError("Incorrect password")
    
    raise InputError("Email is not registered")

def auth_register_v1(email, password, name_first, name_last):
    return {
        'auth_user_id': 1,
    }

from src.data_store import data_store
from src.error import InputError

import re

regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'

def auth_login_v1(email, password):
    store = data_store.get()

    for user in store['users']:
        if user['email'] == email:
            if user['password'] == password:
                return {
                    'auth_user_id': user['id'],
                }
            else:
                raise InputError("Incorrect password")
    
    raise InputError("Email is not registered")

def auth_register_v1(email, password, name_first, name_last):
    if not re.fullmatch(regex, email):
        raise InputError("Invalid email")

    if len(password) < 6:
        raise InputError("Password must be at least 6 characters long")
    
    if len(name_first) < 1:
        raise InputError("First name must be at least 1 character long")
    elif len(name_first) > 50:
        raise InputError("First name cannot be longer than 50 characters")

    if len(name_last) < 1:
        raise InputError("First name must be at least 1 character long")
    elif len(name_last) > 50:
        raise InputError("First name cannot be longer than 50 characters")

    store = data_store.get()

    for user in store['users']:
        if user['email'] == email:
            raise InputError("Email address already in use")

    auth_user_id = len(store['users']) + 1
    user_dict = {'id': auth_user_id, 'email': email, 'password': password, 'name_first': name_first, 'name_last': name_last}

    store['users'].append(user_dict)
    data_store.set(store)
    
    return {
        'auth_user_id': auth_user_id,
    }

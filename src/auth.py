from src.data_store import data_store
from src.error import InputError
from src import helpers

import re
import hashlib

'''
auth.py: This file contains all functions relating to auth endpoints.

Auth Functions:
    - auth_login_v2(email, password)
    - auth_register_v2(email, password, name_first, name_last)
    - auth_logout_v1(token)

Auth Helper functions:
    - generate_handle(name_first, name_last)
'''

regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'

def auth_login_v2(email, password):
    '''
    auth_login_v2: Given a registered user's email and password, returns their `auth_user_id` value

    Arguments:
        email (str)     - email address of a user
        password (str)  - password of a user

    Exceptions:
        InputError      - Occurs when email entered does not belong to a user
                        - Occurs when password is not correct

    Return Value:
        Returns {auth_user_id, token} on registered email and correct password
    '''
    store = data_store.get()

    # Checking if email has been registered
    for user in store['users']:
        if user['email'] == email:
            # Checking if password given matches the password stored
            if user['password'] == hashlib.sha256(password.encode()).hexdigest():
                session_id = helpers.generate_new_session_id()

                user['session_list'].append(session_id)

                data_store.set(store)
                return {
                    'auth_user_id': user['id'],
                    'token': helpers.generate_jwt(user['id'], session_id)
                }
            else:
                raise InputError(description="Incorrect password")
    
    raise InputError(description="Email is not registered")

def auth_register_v2(email, password, name_first, name_last):
    '''
    auth_register_v2: Given a user's first and last name, email address, and password, create a new account for them and return a new `auth_user_id`

    Arguments:
        email (str)         - email of a user
        password (str)      - password of a user
        name_first (str)    - user's first name
        name_last (str)     - user's last name

    Exceptions:
        InputError      - Occurs when email entered is not a valid email
                        - Occurs when email address is already being used by another user
                        - Occurs when length of password is less than 6 characters
                        - Occurs when length of name_first is not between 1 and 50 characters inclusive
                        - Occurs when length of name_last is not between 1 and 50 characters inclusive
                        - Occurs when both name_first and name_last do not contain any alphanumeric characters

    Return Value:
        Returns {auth_user_id, token} on valid email, password, name_first and name_last
    '''
    # Checking if email is valid
    if not re.fullmatch(regex, email):
        raise InputError(description="Invalid email")

    if len(password) < 6:
        raise InputError(description="Password must be at least 6 characters long")
    
    if len(name_first) < 1 or len(name_first) > 50:
        raise InputError(description="First name must be between 1 and 50 characters long")

    if len(name_last) < 1 or len(name_last) > 50:
        raise InputError(description="Last name must be between 1 and 50 characters long")

    store = data_store.get()

    # Checking if email address is already in use
    user_email_list =  helpers.filter_data_store(store_list='users', key='email')

    if email in user_email_list:
       raise InputError(description="Email address already in use")

    handle_str = generate_handle(name_first, name_last)

    # Setting the first registered user to owner (id 1) otherwise member (id 2)
    permission_id = 2
    if len(store['users']) + len(store['removed_users']) == 0:
        permission_id = 1

    auth_user_id = len(store['users']) + len(store['removed_users']) + 1
    session_id = helpers.generate_new_session_id()
    token = helpers.generate_jwt(auth_user_id, session_id)

    # Add user to data store
    
    user_dict = {
        'id': auth_user_id,
        'email': email,
        'password': hashlib.sha256(password.encode()).hexdigest(),
        'name_first': name_first,
        'name_last': name_last,
        'handle_str': handle_str,
        'permission_id': permission_id,
        'session_list': [session_id],
        'notifications': []
    }

    store['users'].append(user_dict)
    data_store.set(store)
    
    return {
        'auth_user_id': auth_user_id,
        'token': token
    }

def auth_logout_v1(token):
    '''
    auth_logout_v1: Given an active token, invalidates the token to log the user out

    Arguments:
        token (str)     - token of a user

    Exceptions:
        AccessError     - Occurs when an invalid token is passed

    Return Value:
        Returns {} on valid token
    '''
    store = data_store.get()

    validate_return = helpers.validate_token(token)

    user_id = validate_return['user_id']
    session_id = validate_return['session_id']

    for user in store['users']:
        if user['id'] == user_id:
            user['session_list'].remove(session_id)

    data_store.set(store)

    return {}

def generate_handle(name_first, name_last):
    '''
    generate_handle: Generates unique handle_str using name_first and name_last
    '''
    handle_str = (name_first + name_last).lower()
    handle_str = re.sub('[^0-9a-z]+', '', handle_str)[:20]

    if len(handle_str) == 0:
        raise InputError(description="First name and last name do not contain any alphanumeric characters")

    # If there is 1 of the same handle, add a 0 to the end
    # If there is more than 1 of the same handle, remove the last character and add the count
    user_handle_list = helpers.filter_data_store(store_list='users', key='handle_str')
    handle_count = 0
    while handle_str in user_handle_list:
        if handle_count > 0:
            handle_str = handle_str[:-len(str(handle_count - 1))] + str(handle_count)
        else:
            handle_str = handle_str + str(handle_count)
        handle_count += 1
    
    return handle_str
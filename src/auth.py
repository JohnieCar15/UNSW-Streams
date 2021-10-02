from src.data_store import data_store
from src.error import InputError

import re

regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'

'''
auth_login_v1: Given a registered user's email and password, returns their `auth_user_id` value

Arguments:
    email (str)     - email address of a user
    password (str)  - password of a user

Exceptions:
    InputError      - Occurs when email entered does not belong to a user
                    - Occurs when password is not correct

Return Value:
    Returns auth_user_id on registered email and correct password
'''
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

'''
auth_register_v1: Given a user's first and last name, email address, and password, create a new account for them and return a new `auth_user_id`

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
    Returns auth_user_id on valid email, password, name_first and name_last
'''
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

    handle_str = (name_first + name_last).lower()
    handle_str = re.sub('[^0-9a-z]+', '', handle_str)[:20]

    if len(handle_str) == 0:
        raise InputError("First name and last name do not contain any alphanumeric characters")

    handle_count = 0

    for user in store['users']:
        if user['email'] == email:
            raise InputError("Email address already in use")

        if user['handle_str'] == handle_str:
            if handle_count > 0:
                handle_str = handle_str[:-1] + str(handle_count)
            else:
                handle_str = handle_str + str(handle_count)

            handle_count += 1

    permission_id = 2
    if len(store['users']) == 0:
        permission_id = 1

    auth_user_id = len(store['users']) + 1
    user_dict = {'id': auth_user_id, 'email': email, 'password': password, 'name_first': name_first, 'name_last': name_last, 'handle_str': handle_str, 'permission_id': permission_id}

    store['users'].append(user_dict)
    data_store.set(store)
    
    return {
        'auth_user_id': auth_user_id,
    }

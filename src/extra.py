from datetime import datetime, timezone
from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import validate_token, filter_data_store
from src import config

'''
extra.py: This file contains all functions relating to extra features.

User Functions:
    - user_status_v1(token, u_id)
    - user_setstatus_v1(token, user_status)

User helper functions:
    - get_status(user, time_need_to_be_away)
'''

def user_status_v1(token, u_id):
    '''
    user_status_v1: For a valid user, return user_status for user with specific u_id

    Arguments:
        token  - string    - token of the user
        u_id   - integer   - auth_user_id of the user

    Exceptions: 
        AccessError - Occurs when token is invalid
        InputError  - Occurs when u_id does not refer to a valid user

    Return Value:
        Returns a string of valid user_status, the valid user_status are: 
            'available', 'away', 'be right back', 'busy', 'do not disturb', 'offline'
    
        For example: { 'user_status': 'busy' }               
    '''
    # get the data_store
    store = data_store.get()

    # Checking if token is valid
    # if token can not be decoded
    # raise AccessError(description="Invalid token")
    validate_token(token)

    # check if u_id is valid
    # Filters data store for correct u_id
    user = filter_data_store(store_list='users', key='id', value=u_id)
    if user == []:
        raise InputError(description="Invalid u_id")
    
    # set the time need (in seconds) for user_status to be 'away' after the user's last opration
    time_need_to_be_away = 5

    # get user_status
    user_status = get_status(user[0], time_need_to_be_away)
    data_store.set(store)
    return {'user_status' : user_status}

def user_setstatus_v1(token, user_status):
    '''
    user_setstatus_v1: For a valid user, Set the user_status of that user.

    Arguments:
        token           - string    - token of the user
        user_status     - string    - one of below strings: 
                                    'available', 'away', 'be right back',
                                    'busy', 'do not disturb', 'offline'

    Exceptions: 
        AccessError     - Occurs when token is invalid
        InputError      - Occurs when user_status is invalid

    Return Value:
        Returns { }               
    '''
    # get the data_store
    store = data_store.get()

    # Checking if token is valid, get the u_id of user
    # if token can not be decoded
    # raise AccessError(description="Invalid token")
    u_id = validate_token(token)['user_id']

    # check if user_status is valid
    valid_status = ['available', 'away', 'be right back', 'busy', 'do not disturb', 'offline']
    if user_status not in valid_status:
        raise InputError(description="Invalid user_status")

    # Filters data store for correct u_id
    user = filter_data_store(store_list='users', key='id', value=u_id)[0]
    
    # set user_status
    # previous_status = user['user_status']
    user['user_status'] = user_status
    user['status_manually_set'] = True
    data_store.set(store)
    return {}

# helper fuunctions:
def get_status(user, time_need_to_be_away):
    user_status = user['user_status']
    # if now is more than and including an hour after the user's last opration
    # set the user_status to be 'away', except the user is 'offline' or 'busy'
    if user['user_status'] != 'offline' and user['user_status'] != 'busy'\
        and (int(datetime.now(timezone.utc).timestamp()) - user['last_opration_time_stamp']) >= time_need_to_be_away:
        user['user_status'] = 'away'
        user_status = user['user_status']
    return user_status

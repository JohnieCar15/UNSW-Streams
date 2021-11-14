import pytest
import requests
import time
from src import config
from src.error import AccessError, InputError

'''
user_setstatus_v1_test.py: All functions related to testing the user_setstatus_v1 function
'''
# define the global variable for valid user_status str
VALID_STATUS = ['available', 'away', 'be right back', 'busy', 'do not disturb', 'offline']

# clear and registers first user
@pytest.fixture
def clear_and_register_user0():
    '''
    clear the data_store and regiter first user: user0
    '''
    clear()
    user0 = user_register('0000@unsw.edu.au', 'password', 'firstname0', 'lastname0')
    return user0



# test invalid token with invalid uid, this should raise AccessError
def test_invalid_token_invalid_user_status(clear_and_register_user0):
    '''
    test if the user_setstatus_v1 raise AccessError
    when both token and user_status are invalid
    '''
    user0 = clear_and_register_user0
    auth_logout(user0)
    input = {
        'token': user0['token'],
        'user_status': 'user_status'
    }
    assert requests.put(config.url + 'user/setstatus/v1', json=input).status_code == AccessError.code
    
# test invalid token with valid uid, and this should raise AccessError
def test_invaild_token_valid_user_status(clear_and_register_user0):
    '''
    test if the user_setstatus_v1 raise AccessError
    when token invalid, but user_status valid
    '''
    user0 = clear_and_register_user0
    auth_logout(user0)
    input = {
        'token': user0['token'],
        'user_status': 'busy'
    }
    assert requests.put(config.url + 'user/setstatus/v1', json=input).status_code == AccessError.code

# test invalid uid and this should raise InputError
def test_vaild_token_invalid_user_status(clear_and_register_user0):
    '''
    test if the user_setstatus_v1 raise InputError
    when u_id invalid, but user_status valid
    '''
    user0 = clear_and_register_user0
    input = {
        'token': user0['token'],
        'user_status': 'user_status'
    }
    assert requests.put(config.url + 'user/setstatus/v1', json=input).status_code == InputError.code

def test_basic_case_for_all_valid_status(clear_and_register_user0):
    '''
    test behaviour of user_status_v1 for all valid status
    '''
    # test the status after register user0
    user0 = clear_and_register_user0
    user1 = user_register('0001@unsw.edu.au', 'password', 'firstname1', 'lastname1')
    assert user_status(user0, user0)['user_status'] == 'available'
    # set and test all the valid user_status
    for status in VALID_STATUS:
        user_setstatus(user0, status)
        assert user_status(user1, user0)['user_status'] == status

  
def test_setstatus_in_standup(clear_and_register_user0):
    '''
    test behaviour of user_setstatus_v1 in_standup 
        when the user is attend a standup: the user will be busy,
            and be available after the standup
        But when this uer set status in a standup,
            then the user_status will change to the staus set by the user
            and remain the set status after the standup
    '''
    # register user0
    user0 = clear_and_register_user0

    # create channel_0
    channel_0 = channel_create(user0, 'channel_0', True)
    
    # in channel_0 user0 start a 2-second standup
    standup_start(user0, channel_0, 2)

    # check the user_status of user0
    # user0 should be 'busy' in the standup
    assert user_status(user0, user0)['user_status'] == 'busy'

    # set the status of user0 to be 'do not disturb', and test the status
    user_setstatus(user0, 'do not disturb')
    assert user_status(user0, user0)['user_status'] == 'do not disturb'

    # test if user_status remain 'do not disturb' after the standup
    time.sleep(2)
    assert user_status(user0, user0)['user_status'] == 'do not disturb'


def test_setstatus_in_second_session(clear_and_register_user0):
    '''
    test behaviour of user_setstatus_v1 when user has more than one session
    '''
    # register user0
    user0 = clear_and_register_user0
    # user0 ogin in another device
    user0_second_session = auth_login('0000@unsw.edu.au', 'password')
    user_setstatus(user0_second_session, 'do not disturb')
    assert user_status(user0, user0)['user_status'] == 'do not disturb'
    assert user_status(user0_second_session, user0)['user_status'] == 'do not disturb'


# below is the helper functions for calling the functions in server for test
def user_setstatus(user, user_status):
    '''
    set the status of user to specific user_status
    '''
    input = {
        'token': user['token'],
        'user_status': user_status,
    }
    requests.put(config.url + 'user/setstatus/v1', json=input).json()


def user_status(user, specific_user):
    '''
    get the status of user with specific u_id and return {'user_status': user_status}
    '''
    input = {
        'token': user['token'],
        'u_id': specific_user['auth_user_id'],
    }
    return requests.get(config.url + 'user/status/v1', params=input).json()


def user_register(email, password, name_first, name_last):
    '''
    register a user and return {'token': token, 'auth_user_id': u_id}
    '''
    input = {
        'email': email,
        'password': password,
        'name_first': name_first,
        'name_last': name_last
    }
    return requests.post(config.url + 'auth/register/v2', json=input).json()


def auth_login(email, password):
    '''
    login the user
    '''
    auth_login_input = {
        'email': email,
        'password': password
    }
    return requests.post(config.url + 'auth/login/v2', json=auth_login_input).json()

def auth_logout(user):
    '''
    logout the user
    '''
    input = {
        'token': user['token']
    }
    requests.post(config.url + 'auth/logout/v1', json=input).json()

def channel_create(creator, name, is_public):
    '''
    create a channel and return {'channel_id': channel_id}
    '''
    input = {
        'token': creator['token'],
        'name': name,
        'is_public': is_public
    }
    return requests.post(config.url + 'channels/create/v2', json=input).json()


def channel_join(user,channel):
    '''
    user join channel by channel_id
    '''
    input = {
        'token': user['token'],
        'channel_id': channel['channel_id'],
    }
    requests.post(config.url + 'channel/join/v2', json=input)


def dm_create(creator, list_of_invitee):
    '''
    create a dm and return {'dm_id': dm_id}
    '''
    input = {
        'token': creator['token'],
        'u_ids': [user['auth_user_id'] for user in list_of_invitee]
    }
    return requests.post(config.url + 'dm/create/v1', json=input).json()


def standup_start(user, channel, length):
    '''
    helper function for standup_start
    '''
    input = {
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'length': length,
    }
    return requests.post(config.url + 'standup/start/v1',json=input).json()


def standup_send(user, channel, message):
    '''
    helper function for standup_send
    '''
    input = {
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': message,
    }
    return requests.post(config.url + 'standup/send/v1',json=input).json()


def clear():
    '''
    reset the data_store and global variables
    '''
    requests.delete(config.url + 'clear/v1')

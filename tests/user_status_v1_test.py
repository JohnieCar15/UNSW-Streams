import pytest
import requests
import time
from src import config
from src.error import AccessError, InputError

'''
user_status_v1_test.py: All functions related to testing the user_status_v1 function
'''

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
def test_invalid_token_and_invalid_uid(clear_and_register_user0):
    '''
    test if the user_status_v1 raise AccessError
    when both token and u_id are invalid
    '''
    user0 = clear_and_register_user0
    auth_logout(user0)
    input = {
        'token': user0['token'],
        'u_id': user0['auth_user_id'] + 1
    }
    assert requests.get(config.url + 'user/status/v1', params=input).status_code == AccessError.code
    
# test invalid token with valid uid, and this should raise AccessError
def test_invaild_token_and_valid_uid(clear_and_register_user0):
    '''
    test if the user_status_v1 raise AccessError
    when token invalid, but u_id valid
    '''
    user0 = clear_and_register_user0
    auth_logout(user0)
    input = {
        'token': user0['token'],
        'u_id': user0['auth_user_id']
    }
    assert requests.get(config.url + 'user/status/v1', params=input).status_code == AccessError.code

# test invalid uid and this should raise InputError
def test_vaild_token_and_invalid_uid(clear_and_register_user0):
    '''
    test if the user_status_v1 raise InputError
    when u_id invalid, but token valid
    '''
    user0 = clear_and_register_user0
    input = {
        'token': user0['token'],
        'u_id': user0['auth_user_id'] + 1
    }
    assert requests.get(config.url + 'user/status/v1', params=input).status_code == InputError.code

def test_status_after_register_login_and_logout(clear_and_register_user0):
    '''
    test behaviour of user_status_v1 for 
        auth_register_v2
        auth_login_v2
        auth_logout_v1
    '''
    # test the status after register user0
    user0 = clear_and_register_user0
    # register user1
    user1 = user_register('0001@unsw.edu.au', 'password', 'firstname1', 'lastname1')
    assert user_status(user0, user0)['user_status'] == 'available'
    assert user_status(user1, user0)['user_status'] == 'available'

    # test the status after user0 logout all sessions
    auth_logout(user0)
    assert user_status(user1, user0)['user_status'] == 'offline'

    # test the status after user0 login
    user0 = auth_login('0000@unsw.edu.au', 'password')
    assert user_status(user0, user0)['user_status'] == 'available'
    assert user_status(user1, user0)['user_status'] == 'available'

    # test the status after user0 login with the second session
    user0_second_session = auth_login('0000@unsw.edu.au', 'password')
    assert user_status(user0, user0)['user_status'] == 'available'
    assert user_status(user1, user0)['user_status'] == 'available'

    # test the status after user0 logout one session
    auth_logout(user0)
    assert user_status(user1, user0)['user_status'] == 'available'

    # test the status after user0 logout all sessions
    auth_logout(user0_second_session)
    assert user_status(user1, user0)['user_status'] == 'offline'
  
def test_status_in_and_after_standup(clear_and_register_user0):
    '''
    test behaviour of user_status_v1 for 
        standup_start_v1
        standup_send_v1
        also the status after the standup
    '''
    # register user0 and user1
    user0 = clear_and_register_user0
    user1 = user_register('0001@unsw.edu.au', 'password', 'firstname1', 'lastname1')

    # create two channel called channel_1 and channel_2
    channel_0 = channel_create(user0, 'channel_0', True)
    channel_1 = channel_create(user1, 'channel_1', True)
    
    # join user0 and user1 to both channels
    channel_join(user0,channel_1)
    channel_join(user1,channel_0)

    # in channel_0 user0 start a 2-second standup
    standup_start(user0, channel_0, 2)
    # check the user_status of user0 and user1
    # user0 should be 'busy' in the standup
    # user1 should be 'available', 
    # after user1 send his/her first message the standup,
    # user will cahnge to busy
    assert user_status(user1, user0)['user_status'] == 'busy'
    assert user_status(user1, user1)['user_status'] == 'available'
    standup_send(user1, channel_0, '0')
    assert user_status(user1, user1)['user_status'] == 'busy'

    # after the standup finish, user0 and user1 should be 'available'
    time.sleep(2)
    assert user_status(user1, user0)['user_status'] == 'available'
    assert user_status(user1, user1)['user_status'] == 'available'

    # now start more complex test: when there are two standups in two channels
    # test uer0 in two standups and one of standup finish eraly
    assert user_status(user1, user0)['user_status'] == 'available'
    standup_start(user0, channel_0, 2)
    standup_start(user0, channel_1, 4)
    assert user_status(user1, user0)['user_status'] == 'busy'
    time.sleep(2)

    # though the standup in channel_0 is finished,
    # user0 is still in standup in channel_1
    assert user_status(user1, user0)['user_status'] == 'busy'

    # after all standups containing user0 is finished,
    # user0 is 'available', unless the user set status duing the standup
    user_setstatus(user0, 'be right back')
    time.sleep(2)
    assert user_status(user1, user0)['user_status'] == 'be right back'

    
def test_one_hour_after_last_action(clear_and_register_user0):
    '''
    test if user_status become 'away' one_hour_after_last_action
    test if user_status become 'available' again, after the user is back
        by do an action after be 'away'
    
    !!! NOTE this test can not be running due to the time limit on SEC machine
    And this will decrease the code coverage.
    But this test has be done by setting the time needed to become 'away' be 5s 
        to do the test with smaller time gap change line 177 time.sleep(3600) in this test,
        and change 'time_need_to_be_away' at line 51 in extra.py
    '''
    # test the status after register user0 and user1
    user0 = clear_and_register_user0
    user1 = user_register('0001@unsw.edu.au', 'password', 'firstname1', 'lastname1')
    assert user_status(user1, user0)['user_status'] == 'available'
    user_setstatus(user0, 'do not disturb')
    assert user_status(user1, user0)['user_status'] == 'do not disturb'

    # user0 is away after an hour (5 seconds for test)
    # IMPORT:
    # note here user_status(user0, user0) should not be call since it will update the user0's
    # last action's time_stamp, to test this user_status(another_user, user0)
    
    time.sleep(5)
    # actual test
    # time.sleep(3600)
    assert user_status(user1, user0)['user_status'] == 'away'

    # when user0 is back and do any action (create a channel here)
    # test if user0 is 'available'
    channel_create(user0, 'channel_1', True)
    assert user_status(user1, user0)['user_status'] == 'available'


# below is the helper functions for calling the functions in server for test

def user_status(user, specific_user):
    '''
    get the status of user with specific u_id and return {'user_status': user_status}
    '''
    input = {
        'token': user['token'],
        'u_id': specific_user['auth_user_id'],
    }
    return requests.get(config.url + 'user/status/v1', params=input).json()

def user_setstatus(user, user_status):
    '''
    set the status of user to specific user_status
    '''
    input = {
        'token': user['token'],
        'user_status': user_status,
    }
    requests.put(config.url + 'user/setstatus/v1', json=input).json()


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

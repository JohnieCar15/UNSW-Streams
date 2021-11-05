import pytest
import requests
from src import config 
from src.error import AccessError, InputError
from datetime import datetime
import time

@pytest.fixture 
def clear_and_register_channel():
    '''
    clears then registers a user, the user also creates a channel 
    '''
    requests.delete(config.url + 'clear/v1')
    register = requests.post(config.url + 'auth/register/v2', json={
        'email': "yes@yes.com", 
        'password': "aaaaaa", 
        'name_first': "firstname", 
        "name_last": "lastname"
    })
    register_data = register.json()
    token = register_data['token']

    channel_create = requests.post(config.url + 'channels/create/v2', json={
        'token': token, 
        'name': 'name', 
        'is_public': True
    })
    channel_create_data = channel_create.json()
    channel_id = channel_create_data['channel_id']

    return {
        'token': token, 
        'u_id': register_data['auth_user_id'], 
        'channel_id': channel_id
        }

def test_successful_case(clear_and_register_channel):
    '''
    Test when no errors and returns correct time_finish
    '''
    # get token and channel_id from fixture
    token = clear_and_register_channel['token']
    channel_id = clear_and_register_channel['channel_id']
    #call standup_start
    standup_start = requests.post(config.url + 'standup/start/v1',json={
        'token': token,
        'channel_id': channel_id,
        'length': 60,
    }).json()
    # calculate time_finish
    time_finish = int(datetime.utcnow().timestamp() + 60)
    assert standup_start['time_finish'] == time_finish

def test_successful_case_after_time_finish(clear_and_register_channel):
    '''
    Testing success case after first standup ends to ensure standup ends properly
    '''
    # get token and channel_id from fixture
    token = clear_and_register_channel['token']
    channel_id = clear_and_register_channel['channel_id']
    # call standup_start with length of one
    standup_start = requests.post(config.url + 'standup/start/v1',json={
        'token': token,
        'channel_id': channel_id,
        'length': 1,
    })
    time.sleep(1)
    # check standup_start return correct time_finish after first standup has ended
    standup_start = requests.post(config.url + 'standup/start/v1',json={
        'token': token,
        'channel_id': channel_id,
        'length': 60,
    }).json()
    time_finish = int(datetime.utcnow().timestamp() + 60)
    assert standup_start['time_finish'] == time_finish

def test_invalid_channel_id(clear_and_register_channel):
    '''
    Testing when an invalid channel_id is passed, should raise InputError
    '''
    token = clear_and_register_channel['token']
    channel_id = clear_and_register_channel['channel_id']

    standup_start = requests.post(config.url + 'standup/start/v1', json={
        'token': token,
        'channel_id': channel_id + 1,
        'length': 60 
    })
    assert standup_start.status_code == InputError.code

def test_invalid_length(clear_and_register_channel):
    '''
    Testing when an invalid length( a negative integer ) is passed, should return InputError
    '''
    token = clear_and_register_channel['token']
    channel_id = clear_and_register_channel['channel_id']

    standup_start = requests.post(config.url + 'standup/start/v1',json={
        'token': token,
        'channel_id': channel_id,
        'length': -60,
    })
    assert standup_start.status_code == InputError.code

def test_active_standup_already(clear_and_register_channel):
    '''
    Testing when an active standup is already in progress, should return InputError
    '''
    token = clear_and_register_channel['token']
    channel_id = clear_and_register_channel['channel_id']

    requests.post(config.url + 'standup/start/v1',json={
        'token': token,
        'channel_id': channel_id,
        'length': 60,
    })

    standup_start = requests.post(config.url + 'standup/start/v1', json={
        'token': token,
        'channel_id': channel_id,
        'length': 60 
    })
    assert standup_start.status_code == InputError.code

def test_not_a_member(clear_and_register_channel):
    '''
    Testing when user who called standup_start isn't a member of the channel, should raise AccessError
    '''
    channel_id = clear_and_register_channel['channel_id']

    register_2 = requests.post(config.url + 'auth/register/v2', json={
        'email': "yes2@yes.com", 
        'password': "aaaaaa", 
        'name_first': "name", 
        "name_last": "name"
    })
    register_2_data = register_2.json()
    token_2 = register_2_data['token']
    # calling standup_start with token of non-member
    standup_start = requests.post(config.url + 'standup/start/v1', json={
        'token': token_2,
        'channel_id': channel_id,
        'length': 60 
    })

    assert standup_start.status_code == AccessError.code

def test_not_a_member_negative_length(clear_and_register_channel):
    '''
    Testing a non_member calling standup_start and an invalid length is also passed, should raise AccessError
    '''
    channel_id = clear_and_register_channel['channel_id']

    register_2 = requests.post(config.url + 'auth/register/v2', json={
        'email': "yes2@yes.com", 
        'password': "aaaaaa", 
        'name_first': "name", 
        "name_last": "name"
    })
    register_2_data = register_2.json()
    token_2 = register_2_data['token']

    standup_start = requests.post(config.url + 'standup/start/v1', json={
        'token': token_2,
        'channel_id': channel_id,
        'length': -60 
    })

    assert standup_start.status_code == AccessError.code

def test_not_a_member_active_standup(clear_and_register_channel):
    '''
    Testing when non_member calls standup_start and there is also an active standup in channel, should raise AccessError
    '''
    token = clear_and_register_channel['token']
    channel_id = clear_and_register_channel['channel_id']

    requests.post(config.url + 'standup/start/v1',json={
        'token': token,
        'channel_id': channel_id,
        'length': 60,
    }).json()

    register_2 = requests.post(config.url + 'auth/register/v2', json={
        'email': "yes2@yes.com", 
        'password': "aaaaaa", 
        'name_first': "name", 
        "name_last": "name"
    })
    register_2_data = register_2.json()
    token_2 = register_2_data['token']

    standup_start = requests.post(config.url + 'standup/start/v1', json={
        'token': token_2,
        'channel_id': channel_id,
        'length': 60 
    })
    
    assert standup_start.status_code == AccessError.code
    
def test_invalid_token_valid_channel_id():
    '''
    Testing when invalid token but a valid channel is passed, should raise AccessError
    '''
    requests.delete(config.url + 'clear/v1')
    register = requests.post(config.url + 'auth/register/v2', json={
        'email': "yes@yes.com", 
        'password': "aaaaaa", 
        'name_first': "firstname", 
        "name_last": "lastname"
    })
    register_data = register.json()
    token = register_data['token']

    channel_create = requests.post(config.url + 'channels/create/v2', json={
        'token': token, 
        'name': 'name', 
        'is_public': True
    })
    channel_create_data = channel_create.json()
    channel_id = channel_create_data['channel_id']

    standup_start = requests.post(config.url + 'standup/start/v1', json={
        'token': 1,
        'channel_id': channel_id,
        'length': 60 
    })

    assert standup_start.status_code == AccessError.code

def test_invalid_token_invalid_channel_id():
    '''
    Testing when an invalid token and invalid channel id are passed, should raise AccessError
    '''
    requests.delete(config.url + 'clear/v1')
    standup_start = requests.post(config.url + 'standup/start/v1', json={
        'token': 1,
        'channel_id': 1,
        'length': 60 
    })

    assert standup_start.status_code == AccessError.code

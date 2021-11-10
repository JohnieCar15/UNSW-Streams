import pytest
import requests
from src import config 
from src.error import AccessError, InputError
from datetime import datetime, timedelta
import time

@pytest.fixture 
def clear_and_register_channel():
    '''
    clears and then registers a user who creates a channel
    Returns the token of the user
    u_id of the user
    channel_id of the channel created
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

def test_standup_active_sucess(clear_and_register_channel):
    '''
    Testing when a standup is active success case
    '''
    token = clear_and_register_channel['token']
    channel_id = clear_and_register_channel['channel_id']

    requests.post(config.url + 'standup/start/v1',json={
        'token': token,
        'channel_id': channel_id,
        'length': 60,
    })
    cur_time = datetime.utcnow()
    time_finish = int((cur_time + timedelta(seconds = 60)).timestamp())

    standup_active = requests.get(config.url + 'standup/active/v1', params={
        'token': token,
        'channel_id': channel_id
    }).json()
    assert standup_active['is_active'] == True
    assert standup_active['time_finish'] == time_finish

def test_no_standup_active_success(clear_and_register_channel):
    '''
    Testing when there is no standup active success case
    '''
    token = clear_and_register_channel['token']
    channel_id = clear_and_register_channel['channel_id']

    standup_active = requests.get(config.url + 'standup/active/v1', params={
        'token': token,
        'channel_id': channel_id
    }).json()
    assert standup_active['is_active'] == False
    assert standup_active['time_finish'] == None

def test_no_standup_active_success_2(clear_and_register_channel):
    '''
    Testing when there is no standup active after standup has ended success case
    '''
    token = clear_and_register_channel['token']
    channel_id = clear_and_register_channel['channel_id']

    requests.post(config.url + 'standup/start/v1',json={
        'token': token,
        'channel_id': channel_id,
        'length': 1,
    })
    time.sleep(1)
    standup_active = requests.get(config.url + 'standup/active/v1', params={
        'token': token,
        'channel_id': channel_id
    }).json()
    assert standup_active['is_active'] == False
    assert standup_active['time_finish'] == None

def test_invalid_channel(clear_and_register_channel):
    '''
    Testing invalid channel_id case
    '''
    token = clear_and_register_channel['token']
    channel_id = clear_and_register_channel['channel_id']

    standup_active = requests.get(config.url + 'standup/active/v1', params={
            'token': token,
            'channel_id': channel_id + 1
        })
    assert standup_active.status_code == InputError.code

def test_not_a_member(clear_and_register_channel):
    '''
    Testing not a member case
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

    standup_active = requests.get(config.url + 'standup/active/v1', params={
            'token': token_2,
            'channel_id': channel_id
        })
    assert standup_active.status_code == AccessError.code

def test_invalid_token_valid_channel():
    '''
    Testing invalid token passed with a valid channel case
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

    standup_active = requests.get(config.url + 'standup/active/v1', params={
            'token': 1,
            'channel_id': channel_id
        })
    assert standup_active.status_code == AccessError.code
    

def test_invalid_token_invalid_channel():
    '''
    Testing invalid token passed with an invalid channel case
    '''
    requests.delete(config.url + 'clear/v1')
    standup_active = requests.get(config.url + 'standup/active/v1', params={
            'token': 1,
            'channel_id': 1
        })
    assert standup_active.status_code == AccessError.code
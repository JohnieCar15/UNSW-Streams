import pytest
import requests
from src import config 
from src.error import AccessError, InputError
from datetime import datetime, timedelta
import time

@pytest.fixture 
def clear_and_register_channel():
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

    requests.post(config.url + 'standup/start/v1',json={
        'token': token,
        'channel_id': channel_id,
        'length': 5,
    })
    # not sure if correct
    cur_time = datetime.utcnow()
    time_finish = int((cur_time + timedelta(seconds = 60)).timestamp())

    return {
        'token': token, 
        'u_id': register_data['auth_user_id'], 
        'channel_id': channel_id
        'time_finish': time_finish
        }

def test_successful_case_one_user(clear_and_register_channel):
    token = clear_and_register_channel['token']
    channel_id = clear_and_register_channel['channel_id']
    u_id = clear_and_register_channel['u_id']
    time_finish = clear_and_register_channel['time_finish']

    requests.post(config.url + 'standup/send/v1', json={
        'token': token,
        'channel_id': channel_id,
        'message': "hi"
    })

    requests.post(config.url + 'standup/send/v1', json={
        'token': token,
        'channel_id': channel_id,
        'message': "hi2"
    })

    requests.post(config.url + 'standup/send/v1', json={
        'token': token,
        'channel_id': channel_id,
        'message': "hi3"
    })
    time.sleep(5)
    channel_messages = requests.get(config.url + 'channel/messages/v2', params={
        'token': token,
        'channel_id': channel_id,
        'start': 0
    }).json()
    assert channel_messages['messages'][0]['message'] == """firstnamelastname: hi
    firstnamelastname: hi2
    firstnamelastname: hi3"""
    assert channel_messages['messages'][0]['u_id'] == u_id
    assert channel_messages['messages'][0]['time_created'] == time_finish

def test_successful_case_multiple_message_multiple_user(clear_and_register_channel):
    token = clear_and_register_channel['token']
    channel_id = clear_and_register_channel['channel_id']
    u_id = clear_and_register_channel['u_id']
    time_finish = clear_and_register_channel['time_finish']

    register_2 = requests.post(config.url + 'auth/register/v2', json={
        'email': "yes2@yes.com", 
        'password': "aaaaaa", 
        'name_first': "name", 
        "name_last": "name"
    })
    register_2_data = register_2.json()
    token = register_2_data['token']
    u_id_2 = register_2_data['auth_user_id']

    requests.post(config.url + 'channel/invite/v2', json={'token': token, 'channel_id': channel_id, 'u_id': u_id_2})
    
    requests.post(config.url + 'standup/send/v1', json={
        'token': token,
        'channel_id': channel_id,
        'message': "hi"
    })

    requests.post(config.url + 'standup/send/v1', json={
        'token': token_2,
        'channel_id': channel_id,
        'message': "hi2"
    })

    requests.post(config.url + 'standup/send/v1', json={
        'token': token,
        'channel_id': channel_id,
        'message': "hi3"
    })

    time.sleep(5)
    channel_messages = requests.get(config.url + 'channel/messages/v2', params={
        'token': token,
        'channel_id': channel_id,
        'start': 0
    }).json()
    assert channel_messages['messages'][0]['message'] == """firstnamelastname: hi
    namename: hi2
    firstnamelastname: hi3"""
    assert channel_messages['messages'][0]['u_id'] == u_id
    assert channel_messages['messages'][0]['time_created'] == time_finish

def test_invalid_channel_id(clear_and_register_channel):
    token = clear_and_register_channel['token']
    channel_id = clear_and_register_channel['channel_id']
    
    standup_send = requests.post(config.url + 'standup/send/v1', json={
        'token': token,
        'channel_id': channel_id + 1,
        'message': "hi"
    }).json()

    assert standup_send.status_code == InputError.code

def test_invalid_message_long(clear_and_register_channel):
    token = clear_and_register_channel['token']
    channel_id = clear_and_register_channel['channel_id']
    
    standup_send = requests.post(config.url + 'standup/send/v1', json={
        'token': token,
        'channel_id': channel_id,
        'message': 1001*'a'
    }).json()

    standup_send.status_code == InputError.code

def test_no_active_standup():
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

    standup_send = requests.post(config.url + 'standup/send/v1', json={
        'token': token,
        'channel_id': channel_id,
        'message': "hi"
    }).json()

    assert standup_send.status_code == InputError.code

def test_not_member(clear_and_register_channel):
    token = clear_and_register_channel['token']
    channel_id = clear_and_register_channel['channel_id']

    register_2 = requests.post(config.url + 'auth/register/v2', json={
        'email': "yes2@yes.com", 
        'password': "aaaaaa", 
        'name_first': "name", 
        "name_last": "name"
    })
    register_2_data = register_2.json()
    token_2 = register_2_data['token']

    standup_send = requests.post(config.url + 'standup/send/v1', json={
        'token': token_2,
        'channel_id': channel_id,
        'message': "hi"
    }).json()

    assert standup_send.status_code == AccessError.code    

def test_not_member_invalid_message_long(clear_and_register_channel):
    token = clear_and_register_channel['token']
    channel_id = clear_and_register_channel['channel_id']

    register_2 = requests.post(config.url + 'auth/register/v2', json={
        'email': "yes2@yes.com", 
        'password': "aaaaaa", 
        'name_first': "name", 
        "name_last": "name"
    })
    register_2_data = register_2.json()
    token_2 = register_2_data['token']

    standup_send = requests.post(config.url + 'standup/send/v1', json={
        'token': token_2,
        'channel_id': channel_id,
        'message': 1001*'a'
    }).json()

    assert standup_send.status_code == AccessError.code 

def test_invalid_token():
    requests.delete(config.url + 'clear/v1')

    standup_send = requests.post(config.url + 'standup/send/v1', json={
        'token': 1,
        'channel_id': 1,
        'message': 1001*'a'
    }).json()

    assert standup_send.status_code == AccessError.code 
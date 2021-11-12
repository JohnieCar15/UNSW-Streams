import pytest
import requests
from src import config
from src.error import AccessError, InputError
from datetime import datetime
'''
search_v1_test.py: All functions related to testing the search_v1 function
'''
@pytest.fixture
def clear_and_send_messages():
    '''
    fixture that clears and then registers a user.
    User then creates a channel.
    A second user is also created and invited to the channel
    A dm is also created with the first and second user
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

    register_2 = requests.post(config.url + 'auth/register/v2', json={
        'email': "yes2@yes.com", 
        'password': "aaaaaa", 
        'name_first': "name", 
        "name_last": "name"
    })
    register_2_data = register_2.json()
    u_id_2 = register_2_data['auth_user_id']

    requests.post(config.url + 'channel/invite/v2', json={'token': token, 'channel_id': channel_id, 'u_id': u_id_2})
    dm_create = requests.post(config.url + 'dm/create/v1', json={'token': token, 'u_ids': [u_id_2]}).json()

    return {
        'token': token,
        'token_2': register_2_data['token'],
        'auth_user_id': register_data['auth_user_id'],
        'auth_user_id_2': register_2_data['auth_user_id'],
        'channel_id': channel_id,
        'dm_id': dm_create['dm_id'],
    }

def message_dict(message_id, auth_user_id, message):
    '''
    Helper function which returns a dict for a given message 
    '''
    return {
        'message_id': message_id,
        'u_id': auth_user_id,
        'message': message,
        'time_created': int(datetime.utcnow().timestamp()),
        'reacts': [{
            'react_id': 1,
            'u_ids': [],
        }],
        'is_pinned': False
    }

def test_success_case_channel(clear_and_send_messages):
    '''
    Testing success case of messages just from channels 
    '''
    token = clear_and_send_messages['token']
    channel_id = clear_and_send_messages['channel_id']
    token_2 = clear_and_send_messages['token_2']
    auth_user_id = clear_and_send_messages['auth_user_id']
    auth_user_id_2 = clear_and_send_messages['auth_user_id_2']

    # sending first message and creating dictionary for it
    message_one = requests.post(config.url + 'message/send/v1', json={
        'token': token,
        'channel_id': channel_id,
        'message': 'hi1'
    }).json()
    message_one_dict = message_dict(message_one['message_id'], auth_user_id, 'hi1')

    # sending second message and creating dicitonary for it 
    message_two = requests.post(config.url + 'message/send/v1', json={
        'token': token_2,
        'channel_id': channel_id,
        'message': 'hi2'
    }).json()
    message_two_dict = message_dict(message_two['message_id'], auth_user_id_2, 'hi2')

    search = requests.get(config.url + 'search/v1', params={'token': token, 'query_str': 'hi'}).json()
    
    assert message_one_dict in search['messages']
    assert message_two_dict in search['messages']

def test_success_case_dm(clear_and_send_messages):
    '''
    Testing success case of message just from dms 
    '''
    token = clear_and_send_messages['token']
    dm_id = clear_and_send_messages['dm_id']
    token_2 = clear_and_send_messages['token_2']
    auth_user_id = clear_and_send_messages['auth_user_id']
    auth_user_id_2 = clear_and_send_messages['auth_user_id_2']
    # sending first message and creating dictionary for it
    message_one = requests.post(config.url + 'message/senddm/v1', json={
        'token': token,
        'dm_id': dm_id,
        'message': 'hi1'
    }).json()
    message_one_dict = message_dict(message_one['message_id'], auth_user_id, 'hi1')
    # sending second message and creating dictionary for it
    message_two = requests.post(config.url + 'message/senddm/v1', json={
        'token': token_2,
        'dm_id': dm_id,
        'message': 'hi2'
    }).json()
    message_two_dict = message_dict(message_two['message_id'], auth_user_id_2, 'hi2')
    search = requests.get(config.url + 'search/v1', params={'token': token, 'query_str': 'hi'}).json()
    
    assert message_one_dict in search['messages']
    assert message_two_dict in search['messages']

def test_success_case_channel_and_dm(clear_and_send_messages):
    '''
    Testing success case of messages from channel and dms
    '''
    token = clear_and_send_messages['token']
    channel_id = clear_and_send_messages['channel_id']
    dm_id = clear_and_send_messages['dm_id']
    token_2 = clear_and_send_messages['token_2']
    auth_user_id = clear_and_send_messages['auth_user_id']

    c_message_one = requests.post(config.url + 'message/send/v1', json={
        'token': token,
        'channel_id': channel_id,
        'message': 'hi1'
    }).json()
    c_message_one_dict = message_dict(c_message_one['message_id'], auth_user_id, 'hi1')

    requests.post(config.url + 'message/send/v1', json={
        'token': token_2,
        'channel_id': channel_id,
        'message': 'hi2'
    }).json()

    dm_message_one = requests.post(config.url + 'message/senddm/v1', json={
        'token': token,
        'dm_id': dm_id,
        'message': 'hi1'
    }).json()
    dm_message_one_dict = message_dict(dm_message_one['message_id'], auth_user_id, 'hi1')

    requests.post(config.url + 'message/senddm/v1', json={
        'token': token_2,
        'dm_id': dm_id,
        'message': 'hi2'
    }).json()
    
    search = requests.get(config.url + 'search/v1', params={'token': token, 'query_str': 'hi1'}).json()
    assert c_message_one_dict in search['messages']
    assert dm_message_one_dict in search['messages']

def test_invalid_query_string_long(clear_and_send_messages):
    '''
    Testing invalid query str that is 1001 characters
    '''
    token = clear_and_send_messages['token']
    search = requests.get(config.url + 'search/v1', params={'token': token, 'query_str': "a"*1001})
    assert search.status_code == InputError.code

def test_invalid_query_string_short(clear_and_send_messages):
    '''
    Testing invalid query str that is 0 characters
    '''
    token = clear_and_send_messages['token']
    search = requests.get(config.url + 'search/v1', params={'token': token, 'query_str': ""})
    assert search.status_code == InputError.code

def invalid_token_valid_query_string():
    '''
    Testing invalid token passed
    '''
    search = requests.get(config.url + 'search/v1', params={'token': 1, 'query_str': "hello"})
    assert search.status_code == AccessError.code

def invalid_token_invalid_query_string():
    '''
    Testing invalid token passed and invalid query str
    '''
    search = requests.get(config.url + 'search/v1', params={'token': 1, 'query_str': ""})
    assert search.status_code == AccessError.code

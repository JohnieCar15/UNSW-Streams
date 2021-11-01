import pytest
import requests
from src import config
from src.error import AccessError, InputError

@pytest.fixture
def clear_and_send_messages():
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
        'channel_id': channel_id,
        'dm_id': dm_create['dm_id'],
    }

def test_success_case_channel(clear_and_send_messages):
    token = clear_and_send_messages['token']
    channel_id = clear_and_send_messages['channel_id']
    token_2 = clear_and_send_messages['token_2']

    message_one = requests.post(config.url + 'message/send/v1', json={
        'token': token,
        'channel_id': channel_id,
        'message': 'hi1'
    }).json()
    message_id_one = message_one['message_id']

    message_two = requests.post(config.url + 'message/send/v1', json={
        'token': token_2,
        'channel_id': channel_id,
        'message': 'hi2'
    }).json()
    message_id_two = message_two['message_id']

    search = requests.get(config.url + 'search/v1', params={'token': token, 'query_str': 'hi'}).json()
    # not sure what to do for assert statement

    
def test_success_case_dm(clear_and_send_messages):
    token = clear_and_send_messages['token']
    dm_id = clear_and_send_messages['dm_id']
    token_2 = clear_and_send_messages['token_2']

    message_one = requests.post(config.url + 'message/senddm/v1', json={
        'token': token,
        'dm_id': dm_id,
        'message': 'hi1'
    }).json()
    message_id_one = message_one['message_id']

    message_two = requests.post(config.url + 'message/senddm/v1', json={
        'token': token_2,
        'dm_id': dm_id,
        'message': 'hi2'
    }).json()
    message_id_two = message_two['message_id']

    search = requests.get(config.url + 'search/v1', params={'token': token, 'query_str': 'hi'}).json()
    # not sure what to do for assert statement

def test_success_case_channel_and_dm():
    token = clear_and_send_messages['token']
    channel_id = clear_and_send_messages['channel_id']
    dm_id = clear_and_send_messages['dm_id']
    token_2 = clear_and_send_messages['token_2']

    c_message_one = requests.post(config.url + 'message/send/v1', json={
        'token': token,
        'channel_id': channel_id,
        'message': 'hi1'
    }).json()


    c_message_two = requests.post(config.url + 'message/send/v1', json={
        'token': token_2,
        'channel_id': channel_id,
        'message': 'hi2'
    }).json()


    dm_message_one = requests.post(config.url + 'message/senddm/v1', json={
        'token': token,
        'dm_id': dm_id,
        'message': 'hi1'
    }).json()


    dm_message_two = requests.post(config.url + 'message/senddm/v1', json={
        'token': token_2,
        'dm_id': dm_id,
        'message': 'hi2'
    }).json()


#def test_success_case_complex():

def test_invalid_query_string_long(clear_and_send_messages):
    token = clear_and_send_messages['token']
    search = requests.get(config.url + 'search/v1', params={'token': token, 'query_str': "a"*1001}).json()
    assert search.status_code == InputError.code

def test_invalid_query_string_short(clear_and_send_messages):
    token = clear_and_send_messages['token']
    search = requests.get(config.url + 'search/v1', params={'token': token, 'query_str': ""}).json()
    assert search.status_code == InputError.code

def invalid_token_valid_query_string():
    search = requests.get(config.url + 'search/v1', params={'token': 1, 'query_str': "hello"}).json()

def invalid_token_invalid_query_string():
    search = requests.get(config.url + 'search/v1', params={'token': 1, 'query_str': ""}).json()
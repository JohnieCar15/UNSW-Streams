"""import pytest
import requests
import json
from src import config
from src.error import InputError, AccessError

@pytest.fixture
def clear_and_register():
    requests.delete(config.url + 'clear/v1')
    register = requests.post(config.url + 'auth/register/v2', json={'email': 'yes@yes.com', 'password': 'aaaaaa', 'name_first': "firstname", "name_last": "lastname"})
    register_data = register.json()
    return register_data['token']

def test_valid_id_valid_name_public(clear_and_register):
    token = clear_and_register
    channels_create = requests.post(config.url + 'channels/create/v2', json={'token': token, 'name': 'name', 'is_public': True})
    channels_create_data = channels_create.json()
    channels_create_id = channels_create_data['channel_id']
    '''
    channels_list = requests.get(config.url + 'channels/list/v2', params={'token': token})
    channels_list_data = channels_list.json()
    channels_list_id = channels_list_data['channel_id']
    '''
    assert channels_create_id == 1

def test_valid_id_invalid_short_channel_name_public(clear_and_register):
    token = clear_and_register
    channels_create = requests.post(config.url + 'channels/create/v2', json={'token': token, 'name':"" , 'is_public': True})
    # input error 
    assert channels_create.status_code == InputError.code

def test_valid_id_invalid_long_channel_name_public(clear_and_register):
    token = clear_and_register
    channels_create = requests.post(config.url + 'channels/create/v2', json={'token': token, 'name': 'aaaaaaaaaaaaaaaaaaaaa', 'is_public': True})
    # input error
    assert channels_create.status_code == InputError.code

def test_invalid_token_invalid_short_channel_name_public():
    channels_create = requests.post(config.url + 'channels/create/v2', json={'token': 1, 'name':"" , 'is_public': True})
    # access error
    assert channels_create.status_code == AccessError.code

def test_invalid_token_invalid_long_channel_name_public():
    channels_create = requests.post(config.url + 'channels/create/v2', json={'token': 1, 'name': 'aaaaaaaaaaaaaaaaaaaaa', 'is_public': True})
    # access error
    assert channels_create.status_code == AccessError.code

def test_invalid_id_valid_name_public():
    channels_create = requests.post(config.url + 'channels/create/v2', json={'token': 1, 'name': 'name', 'is_public': True})
    # access error 
    assert channels_create.status_code == AccessError.code
"""
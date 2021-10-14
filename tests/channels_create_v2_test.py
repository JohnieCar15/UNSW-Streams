import pytest
import requests
import json
from src import config
from src.other import clear_v2
from src.auth import auth_register_v2
from src.channels import channels_create_v2
from src.channel import channel_details_v2, channel_invite_v2
from src.error import InputError, AccessError

@pytest.fixture
def clear_and_register():
    requests.delete(config.url + 'clear/v2')
    register = requests.post(config.url + 'auth/register/v2', params={'email': 'yes@yes.com', 'password': 'aaaaaa', 'name_first': "firstname", "name_last": "lastname"})
    register_data = register.json()
    return register_data['token']

def test_valid_id_valid_name_public(clear_and_register):
    token = clear_and_register
    channels_create = requests.post(config.url + 'channels/create/v2', params={'token': token, 'name': 'name', 'is_public': True})
    channels_create_data = channel_create.json()
    channels_create_id = channels_create_data['channel_id']

    channels_list = requests.get(config.url + 'channels/list/v2', params={'token': token})
    channels_list_data = channels_list.json()
    channels_list_id = channels_list_data['channel_id']

    assert channels_create_id == channels_list_id[0]['channel_id']

def test_valid_id_invalid_short_channel_name_public(clear_and_register):
    token = clear_and_register
    channels_create = requests.post(config.url + 'channels/create/v2', params={'token': token, 'name':"" , 'is_public': True})
    # input error 
    assert channels_create.status_code == 400

def test_valid_id_invalid_long_channel_name_public(clear_and_register):
    token = clear_and_register
    channels_create = requests.post(config.url + 'channels/create/v2', params={'token': token, 'name': 'aaaaaaaaaaaaaaaaaaaaa', 'is_public': True})
    # input error
    assert channels_create.status_code == 400

def test_invalid_id_invalid_short_channel_name_public(clear_and_register):
    channels_create = requests.post(config.url + 'channels/create/v2', params={'token': 1, 'name':"" , 'is_public': True})
    # access error
    assert channels_create.status_code == 403 

def test_invalid_id_invalid_long_channel_name_public(clear_and_register):
    token = clear_and_register
    channels_create = requests.post(config.url + 'channels/create/v2', params={'token': 1, 'name': 'aaaaaaaaaaaaaaaaaaaaa', 'is_public': True})
    # access error
    assert channels_create.status_code == 403 

def test_invalid_id_valid_name_public():
    channels_create = requests.post(config.url + 'channels/create/v2', params={'token': 1, 'name': 'name', 'is_public': True})
    # access error 
    assert channels_create.status_code == 403

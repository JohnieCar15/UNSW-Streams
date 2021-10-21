import pytest
import requests
import json
from src import config
from src.error import InputError, AccessError

@pytest.fixture
def clear_and_register():
    # clear then register a user 
    requests.delete(config.url + 'clear/v2')
    register = requests.post(config.url + 'auth/register/v2', json={'email': "yes@yes.com", 'password': "aaaaaa", 'name_first': "firstname", "name_last": "lastname"})
    register_data = register.json()

    # create a channel and get its channel id
    channel_create = requests.post(config.url + 'channels/create/v2', json={'token': token, 'name': "name", 'is_public': True})
    channel_create_data = channel_create.json()
    channel_create_data["channel_id"]

    return {'token': register_data["token"], 'channel_id': channel_create_data["channel_id"]}


# testing a valid channel called by authorised member
def test_valid_channel_authorised(clear_and_register):
    token = clear_and_register['token']
    channel_id = clear_and_register['channel_id']
    channel_leave = requests.post(config.url + 'channel/leave/v1', json={'token': token, 'channel_id': channel_id})
    channel_leave_data = channel_leave.json()
    assert channel_leave_data == {}
    channel_details = requests.get(config.url + 'channel/details/v1', json={'token': token, 'channel_id': channel_id})
    assert channel_details.status_code == AccessError.code


# testing a valid channel calleed by an unauthorised member
def test_valid_channel_unauthorised(clear_and_register):
    channel_id = clear_and_register['channel_id']
    register = requests.post(config.url + 'auth/register/v2', json={'email': "yes2@yes.com", 'password': "aaaaaa", 'name_first': "name", "name_last": "name"})
    register_data = register.json()
    token_2 = register_data['token']
    channel_leave = requests.post(config.url + 'channel/leave/v1', json={'token': token_2, 'channel_id': channel_id})
    assert channel_leave.status_code == AccessError.code

# testing a valid channel called by an invalid id 
def test_valid_channel_invalid_token(clear_and_register):
    token = clear_and_register['token']
    channel_id = clear_and_register['channel_id']
    channel_leave = requests.post(config.url + 'channel/leave/v1', json={'token': token + 1, 'channel_id': channel_id})
    assert channel_leave.status_code == AccessError.code

# testing an invalid channel called by valid token
def test_invalid_channel_valid_token():
    requests.delete(config.url + 'clear/v2')
    register = requests.post(config.url + 'auth/register/v2', json={'email': "yes@yes.com", 'password': "aaaaaa", 'name_first': "firstname", "name_last": "lastname"})
    register_data = register.json()
    token = register_data['token']
    channel_leave = requests.post(config.url + 'channel/leave/v1', json={'token': token, 'channel_id': 1})
    assert channel_leave.status_code == InputError.code

# testing an invalid channel called by invalid token
def test_invalid_channel_invalid_token():
    requests.delete(config.url + 'clear/v2')
    channel_leave = requests.post(config.url + 'channel/leave/v1', json={'token': 1, 'channel_id': 1})
    assert channel_leave.status_code == AccessError.code

import pytest
import requests
import json
from src import config
from src.error import InputError, AccessError

@pytest.fixture
def clear_and_register_2_users():
    requests.delete(config.url + 'clear/v2')
    register = requests.post(config.url + 'auth/register/v2', params={'email': 'yes@yes.com', 'password': 'aaaaaa', 'name_first': "firstname", "name_last": "lastname"})
    register_data = register.json()

    register_2 = requests.post(config.url + 'auth/register/v2', params={'email': 'yes2@yes.com', 'password': 'aaaaaa', 'name_first': "name", "name_last": "name"})
    register_2_data = register_2.json()
    return {'token': register_data['token'], 'u_id': register_data['auth_user_id'], 'u_id_2': register_2_data['auth_user_id']}



# valid token and valid u_id
def test_valid_token_valid_u_id(clear_and_register_2_users):
    token = clear_and_register_2_users['token']
    u_id_2 = clear_and_register_2_users['u_id_2']
    dm_create = requests.post(config.url + 'dm/create/v1', params={'token': token, 'u_ids': [u_id_2]})
    dm_create_data = dm_create.json()
    dm_create_id = dm_create_data['dm_id']

    dm_list = requests.get(config.url + 'dm/list/v1', params={'token': token})
    dm_list_data = dm_list.json()
    dm_list_id = dm_list_data['dms']

    assert dm_create_id == dm_list_id[0]['dm_id']
    assert dm_list_id[0]['name'] == 'firstnamelastname, namename'

# valid token and invalid u_id
def test_valid_token_invalid_u_id(clear_and_register_2_users):
    token = clear_and_register_2_users['token']
    token_u_id = clear_and_register_2_users['u_id']
    dm_create = requests.post(config.url + 'dm/create/v1', params={'token': token, 'u_ids': [token_u_id]})
    assert dm_create.status_code == InputError.code

# invalid token and valid u_id
def test_invalid_token_valid_u_id(clear_and_register_2_users):
    u_id_2 = clear_and_register_2_users['u_id_2']
    dm_create = requests.post(config.url + 'dm/create/v1', params={'token': "", 'u_ids': [u_id_2]})
    assert dm_create.status_code == AccessError.code

# invalid token and invalid u_id
def test_invalid_token_invalid_u_id():
    requests.delete(config.url + 'clear/v2')
    dm_create = requests.post(config.url +'dm/create/v1', params={'token': '', 'u_ids': [1]})
    assert dm_create.status_code == AccessError.code
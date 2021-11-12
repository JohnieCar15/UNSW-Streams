import pytest
import requests
import json
from src import config
from src.error import InputError, AccessError
from src.data_store import data_store
'''
dm_create_v1_test.py: All functions related to testing the dm_create_v1 function 
'''
@pytest.fixture
def clear_and_register_2_users():
    '''
    Clears and then registers 2 seperate users
    Return the token uid of both users 
    '''
    requests.delete(config.url + 'clear/v1')
    register = requests.post(config.url + 'auth/register/v2', json={'email': 'yes@yes.com', 'password': 'aaaaaa', 'name_first': "firstname", "name_last": "lastname"})
    register_data = register.json()

    register_2 = requests.post(config.url + 'auth/register/v2', json={'email': 'yes2@yes.com', 'password': 'aaaaaa', 'name_first': "name", "name_last": "name"})
    register_2_data = register_2.json()
    return {'token': register_data['token'], 'u_id': register_data['auth_user_id'], 'u_id_2': register_2_data['auth_user_id']}


def test_valid_token_valid_u_id(clear_and_register_2_users):
    '''
    Testing success case 
    '''
    token = clear_and_register_2_users['token']
    u_id_2 = clear_and_register_2_users['u_id_2']
    dm_create = requests.post(config.url + 'dm/create/v1', json={'token': token, 'u_ids': [u_id_2]})
    dm_create_data = dm_create.json()
    dm_create_id = dm_create_data['dm_id']
    dm_list = requests.get(config.url + 'dm/list/v1', params={'token': token})
    dm_list_data = dm_list.json()
    dm_list_id = dm_list_data['dms']

    assert dm_create_id == dm_list_id[0]['dm_id']
    assert dm_list_id[0]['name'] == 'firstnamelastname, namename'

def test_valid_token_invalid_u_id(clear_and_register_2_users):
    ''' 
    Testing invalid u_ids being passed 
    '''
    token = clear_and_register_2_users['token']
    token_u_id = clear_and_register_2_users['u_id']
    dm_create = requests.post(config.url + 'dm/create/v1', json={'token': token, 'u_ids': [token_u_id + 100]})
    assert dm_create.status_code == InputError.code

def test_invalid_token_valid_u_id(clear_and_register_2_users):
    '''
    Testing invalid token passed with valid u_id
    '''
    u_id_2 = clear_and_register_2_users['u_id_2']
    dm_create = requests.post(config.url + 'dm/create/v1', json={'token': "", 'u_ids': [u_id_2]})
    assert dm_create.status_code == AccessError.code

def test_invalid_token_invalid_u_id():
    '''
    Testing invalid token passed with invalid u_id
    '''
    requests.delete(config.url + 'clear/v1')
    dm_create = requests.post(config.url +'dm/create/v1', json={'token': '', 'u_ids': [1]})
    assert dm_create.status_code == AccessError.code
    
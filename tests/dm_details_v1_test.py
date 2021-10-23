import pytest
import requests
import json
from src import config
from src.error import InputError, AccessError


@pytest.fixture
def clear_and_register():
    requests.delete(config.url + 'clear/v1')
    register = requests.post(config.url + 'auth/register/v2', json={'email': "yes@yes.com", 'password': "aaaaaa", 'name_first': "firstname", "name_last": "lastname"})
    register_data = register.json()
    token = register_data['token']
    register_2 = requests.post(config.url + 'auth/register/v2', json={'email': "yes2@yes.com", 'password': "aaaaaa", 'name_first': "name", "name_last": "name"})
    register_2_data = register_2.json()
    u_id_2 = register_2_data['auth_user_id']
    # create a dm and get its dm id
    dm_create = requests.post(config.url + 'dm/create/v1', json={'token': token, 'u_ids': [u_id_2]})
    dm_create_data = dm_create.json()

    return {'token': token, 'dm_id':dm_create_data['dm_id'], 'u_id': register_data['auth_user_id'], 'u_id_2': register_2_data['auth_user_id']}

# a valid dm and authorised member
def test_valid_channel_authorised_member(clear_and_register):
    token = clear_and_register['token']
    dm_id = clear_and_register['dm_id']
    id_num = clear_and_register['u_id']
    id_num_2 = clear_and_register['u_id_2']
    register = requests.post(config.url + 'auth/register/v2', json={'email': "yes3@yes.com", 'password': "aaaaaa", 'name_first': "firstname", "name_last": "lastname"})
    dm_details = requests.get(config.url + 'dm/details/v1', params={'token': token, 'dm_id': dm_id})
    dm_details_data = dm_details.json()
    assert dm_details_data == {
        'name': 'firstnamelastname, namename',
        'members': [
            {
                'u_id': id_num,
                'email': 'yes@yes.com',
                'name_first': 'firstname',
                'name_last': 'lastname',
                'handle_str': 'firstnamelastname',
            } ,

            {
                'u_id': id_num_2,
                'email': 'yes2@yes.com',
                'name_first': 'name',
                'name_last': 'name',
                'handle_str': 'namename',
            }
        ],

    }

# a valid dm and member who isn't part of dm 
def test_valid_channel_authorised_member_2(clear_and_register):
    token = clear_and_register['token']
    dm_id = clear_and_register['dm_id']
    id_num = clear_and_register['u_id']
    id_num_2 = clear_and_register['u_id_2']

    dm_details = requests.get(config.url + 'dm/details/v1', params={'token': token, 'dm_id': dm_id})
    dm_details_data = dm_details.json()
    assert dm_details_data == {
        'name': 'firstnamelastname, namename',
        'members': [
            {
                'u_id': id_num,
                'email': 'yes@yes.com',
                'name_first': 'firstname',
                'name_last': 'lastname',
                'handle_str': 'firstnamelastname',
            } ,

            {
                'u_id': id_num_2,
                'email': 'yes2@yes.com',
                'name_first': 'name',
                'name_last': 'name',
                'handle_str': 'namename',
            }
        ],

    }
# a valid dm and unauthorised member
def test_valid_channel_unauthorised_member(clear_and_register):
    dm_id = clear_and_register['dm_id']
    
    register = requests.post(config.url + 'auth/register/v2', json={'email': "yes3@yes.com", 'password': "aaaaaa", 'name_first': "name", "name_last": "name"})
    register_data = register.json()
    token_2 = register_data["token"]

    dm_details = requests.get(config.url + 'dm/details/v1', params={'token': token_2, 'dm_id': dm_id})
    assert dm_details.status_code == AccessError.code

# a valid dm invalid token
def test_valid_channel_invalid_token(clear_and_register):
    dm_id = clear_and_register['dm_id']
    dm_details = requests.get(config.url + 'dm/details/v1', params={'token': "", "dm_id": dm_id})
    assert dm_details.status_code == AccessError.code

# an invalid dm valid token
def test_nvalid_channel_invalid_token():
    requests.delete(config.url + 'clear/v1')
    register = requests.post(config.url + 'auth/register/v2', json={'email': "yes@yes.com", 'password': "aaaaaa", 'name_first': "firstname", "name_last": "lastname"})
    register_data = register.json()
    token = register_data['token']
    dm_details = requests.get(config.url + 'dm/details/v1', params={'token': token, 'dm_id': 1})
    assert dm_details.status_code == InputError.code
    
# an invalid channel invalid token 
def test_invalid_channel_invalid_token():
    requests.delete(config.url + 'clear/v1')
    dm_details = requests.get(config.url + 'dm/details/v1', params={'token': 1, 'dm_id': 1})
    assert dm_details.status_code == AccessError.code
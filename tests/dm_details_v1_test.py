import pytest
import requests
import json
from src import config
from src.other import clear_v2
from src.auth import auth_register_v2
from src.dm import dm_create_v1, dm_details_v1, dm_invite_v2
from src.error import InputError, AccessError


@pytest.fixture
def clear_and_register():
    requests.delete(config.url + 'clear/v2')
    register = requests.post(config.url + 'auth/register/v2', params={'email': "yes@yes.com", 'password': "aaaaaa", 'name_first': "firstname", "name_last": "lastname"})
    register_data = register.json()

    register_2 = requests.post(config.url + 'auth/register/v2', params={'email': "yes2@yes.com", 'password': "aaaaaa", 'name_first': "name", "name_last": "name"})
    register_2_data = register.json()
    u_id = register_2_data['auth_user_id']
    # create a dm and get its dm id
    dm_create = requests.post(config.url + 'dm/create/v1', params={'token': token, 'u_ids': [u_id]})
    dm_create_data = dm_create.json()
    dm_create_data["dm_id"]

    return register_data["token"], channel_create_data['dm_id']

# a valid channel and authorised member
def valid_channel_authorised_member(clear_and_register):
    token, dm_id = clear_and_register
    dm_details = requests.post(config.url + 'dm/details/v1', params={'token': token, 'dm_id': dm_id})
    dm_details_data = dm_details.json()
    assert dm_details_data == {
        'name': 'firstnamelastname, namename'
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
# a valid channel and unauthorised member
def valid_channel_unauthorised_member(clear_and_register):
    token, dm_id = clear_and_register
    
    register = requests.post(config.url + 'auth/register/v2', params={'email': "yes2@yes.com", 'password': "aaaaaa", 'name_first': "name", "name_last": "name"})
    register_data = register.json()
    token_2 = register_data["token"]

    dm_details = requests.get(config.url + 'dm/details/v1', params={'token': token_2, 'dm_id': dm_id})
    assert dm_details.status_code == 403

# a valid channel invalid token
def valid_channel_invalid_token(clear_and_register):

    dm_details = requests.get(config.url + 'dm/details/v1', params={'token': "", "dm_id": dm_id})
    assert dm_details.status_code == 403

# an invalid channel valid token
def invalid_channel_invalid_token():
    requests.delete(config.url + 'clear/v2')
    register = requests.post(config.url + 'auth/register/v2', params={'email': "yes@yes.com", 'password': "aaaaaa", 'name_first': "firstname", "name_last": "lastname"})
    register_data = register.json()
    token = register_data['token']
    dm_details = requests.get(config.url + 'dm/details/v1', params={'token': token, 'dm_id': 1})
    assert dm_details.status_code == 400
    
# an invalid channel invalid token 
def invalid_channel_invalid_token():
    requests.delete(config.url + 'clear/v2')
    dm_detials = requests.get(config.url + 'dm/details/v1', params={'token': 1, 'dm_id': 1})
    assert dm_details.status_code == 403
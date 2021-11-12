import pytest
import requests
import json
from src import config
from src.error import InputError, AccessError

'''
dm_details_v1_test.py: All functions related to testing the dm_details_v1 function 
'''
@pytest.fixture
def clear_and_register():
    '''
    clears then registers 2 users
    The users are added to a dm 
    '''
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

    return {'token': token, 'dm_id':dm_create_data['dm_id'],'token_2': register_2_data['token'], 'u_id': register_data['auth_user_id'], 'u_id_2': register_2_data['auth_user_id']}

def test_valid_dm_authorised_member(clear_and_register):
    '''
    Testing success case
    '''
    token = clear_and_register['token']
    token_2 = clear_and_register['token_2']
    dm_id = clear_and_register['dm_id']
    id_num = clear_and_register['u_id']
    id_num_2 = clear_and_register['u_id_2']
    requests.post(config.url + 'auth/register/v2', json={'email': "yes3@yes.com", 'password': "aaaaaa", 'name_first': "firstname", "name_last": "lastname"})
    dm_details = requests.get(config.url + 'dm/details/v1', params={'token': token, 'dm_id': dm_id})
    dm_details_data = dm_details.json()
    url_one_data = requests.get(config.url + 'user/profile/v1', params={
        'token': token,
        'u_id': id_num 
    }).json()
    url_one = url_one_data['user']['profile_img_url']
    url_two_data = requests.get(config.url + 'user/profile/v1', params={
        'token': token_2,
        'u_id': id_num_2 
    }).json()
    url_two = url_two_data['user']['profile_img_url']

    assert dm_details_data == {
        'name': 'firstnamelastname, namename',
        'members': [
            {
                'u_id': id_num,
                'email': 'yes@yes.com',
                'name_first': 'firstname',
                'name_last': 'lastname',
                'handle_str': 'firstnamelastname',
                'profile_img_url': url_one
            } ,

            {
                'u_id': id_num_2,
                'email': 'yes2@yes.com',
                'name_first': 'name',
                'name_last': 'name',
                'handle_str': 'namename',
                'profile_img_url': url_two
            }
        ],

    }

def test_valid_dm_authorised_member_2(clear_and_register):
    '''
    Testing success case and there exists a user who isn't part of the dm 
    '''
    token = clear_and_register['token']
    token_2 = clear_and_register['token_2']
    dm_id = clear_and_register['dm_id']
    id_num = clear_and_register['u_id']
    id_num_2 = clear_and_register['u_id_2']

    dm_details = requests.get(config.url + 'dm/details/v1', params={'token': token, 'dm_id': dm_id})
    dm_details_data = dm_details.json()
    url_one_data = requests.get(config.url + 'user/profile/v1', params={
        'token': token,
        'u_id': id_num 
    }).json()
    url_one = url_one_data['user']['profile_img_url']
    url_two_data = requests.get(config.url + 'user/profile/v1', params={
        'token': token_2,
        'u_id': id_num_2 
    }).json()
    url_two = url_two_data['user']['profile_img_url']
    assert dm_details_data == {
        'name': 'firstnamelastname, namename',
        'members': [
            {
                'u_id': id_num,
                'email': 'yes@yes.com',
                'name_first': 'firstname',
                'name_last': 'lastname',
                'handle_str': 'firstnamelastname',
                'profile_img_url': url_one
            } ,

            {
                'u_id': id_num_2,
                'email': 'yes2@yes.com',
                'name_first': 'name',
                'name_last': 'name',
                'handle_str': 'namename',
                'profile_img_url': url_two
            }
        ],

    }

def test_valid_dm_unauthorised_member(clear_and_register):
    '''
    Testing user who calls function isn't a member of the DM 
    '''
    dm_id = clear_and_register['dm_id']
    
    register = requests.post(config.url + 'auth/register/v2', json={'email': "yes3@yes.com", 'password': "aaaaaa", 'name_first': "name", "name_last": "name"})
    register_data = register.json()
    token_2 = register_data["token"]

    dm_details = requests.get(config.url + 'dm/details/v1', params={'token': token_2, 'dm_id': dm_id})
    assert dm_details.status_code == AccessError.code

def test_valid_dm_invalid_token(clear_and_register):
    '''
    Testing an invalid token being passed for a valid dm 
    '''
    dm_id = clear_and_register['dm_id']
    dm_details = requests.get(config.url + 'dm/details/v1', params={'token': "", "dm_id": dm_id})
    assert dm_details.status_code == AccessError.code

def test_invalid_dm_valid_token():
    '''
    Testing an invalid dm being passed 
    '''
    requests.delete(config.url + 'clear/v1')
    register = requests.post(config.url + 'auth/register/v2', json={'email': "yes@yes.com", 'password': "aaaaaa", 'name_first': "firstname", "name_last": "lastname"})
    register_data = register.json()
    token = register_data['token']
    dm_details = requests.get(config.url + 'dm/details/v1', params={'token': token, 'dm_id': 1})
    assert dm_details.status_code == InputError.code
    
def test_invalid_dm_invalid_token():
    '''
    Testing an invalid dm and invalid token being passed
    '''
    requests.delete(config.url + 'clear/v1')
    dm_details = requests.get(config.url + 'dm/details/v1', params={'token': 1, 'dm_id': 1})
    assert dm_details.status_code == AccessError.code
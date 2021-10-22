import pytest
import requests
import json
from src import config
from src.error import InputError, AccessError

@pytest.fixture
def clear_and_register():
    # clear then register a user 
    requests.delete(config.url + 'clear/v1')
    register = requests.post(config.url + 'auth/register/v2', json={'email': "yes@yes.com", 'password': "aaaaaa", 'name_first': "firstname", "name_last": "lastname"})
    register_data = register.json()
    token = register_data['token']

    # create a channel and get its channel id
    channel_create = requests.post(config.url + 'channels/create/v2', json={'token': token, 'name': "name", 'is_public': True})
    channel_create_data = channel_create.json()

    return {'token':register_data["token"], 'u_id': register_data['auth_user_id'], 'channel_id': channel_create_data["channel_id"]}

# testing a valid channel called by authorised member 
def test_valid_channel_authorised(clear_and_register):
    '''
    A test to check channel_details when channel id is valid and called by authorised member 
    '''

    # token for 1st user and channel_id 
    token = clear_and_register['token']
    id_num = clear_and_register['u_id']
    channel_id = clear_and_register['channel_id']

    # call channel details and check it works 
    channel_details = requests.get(config.url + 'channel/details/v2', params={'token': token, 'channel_id': channel_id})
    channel_details_data = channel_details.json()
    assert channel_details_data == {
        'name': 'name',
        'is_public': True,
        'owner_members': [
            {
                'u_id': id_num,
                'email': 'yes@yes.com',
                'name_first': 'firstname',
                'name_last': 'lastname',
                'handle_str': 'firstnamelastname',
            }
        ],
        'all_members': [
            {
                'u_id': id_num,
                'email': 'yes@yes.com',
                'name_first': 'firstname',
                'name_last': 'lastname',
                'handle_str': 'firstnamelastname',
            }
        ],
    }

def test_user_not_a_member(clear_and_register):
    '''
    A test to check channel_details when channel id is valid and called by authorised member and there are users not part of the channel
    '''
    # token for 1st user and channel_id 
    token = clear_and_register['token']
    id_num = clear_and_register['u_id']
    channel_id = clear_and_register['channel_id']

    # register another user who isn't in channel
    requests.post(config.url + 'auth/register/v2', json={'email': "yes3@yes.com", 'password': "aaaaaa", 'name_first': "firstname", "name_last": "lastname"})

    # call channel details and check it works 
    channel_details = requests.get(config.url + 'channel/details/v2', params={'token': token, 'channel_id': channel_id})
    channel_details_data = channel_details.json()
    assert channel_details_data == {
        'name': 'name',
        'is_public': True,
        'owner_members': [
            {
                'u_id': id_num,
                'email': 'yes@yes.com',
                'name_first': 'firstname',
                'name_last': 'lastname',
                'handle_str': 'firstnamelastname',
            }
        ],
        'all_members': [
            {
                'u_id': id_num,
                'email': 'yes@yes.com',
                'name_first': 'firstname',
                'name_last': 'lastname',
                'handle_str': 'firstnamelastname',
            }
        ],
    }
'''
def test_valid_channel_2_members(clear_and_register):
    
    # get token for 1st user
    token = clear_and_register['token']
    channel_id = clear_and_register['channel_id']
    id_num = clear_and_register['u_id']
    # get token for 2nd user
    register = requests.post(config.url + 'auth/register/v2', json={'email': "yes2@yes.com", 'password': "aaaaaa", 'name_first': "name", "name_last": "name"})
    register_data = register.json()
    id_num_2 = register_data["u_id"]

    register = requests.post(config.url + 'channel/invite/v2', json={'token': token, 'channel_id': channel_id, 'u_id': id_num_2})

    # call channel details and check it matches
    channel_details = requests.get(config.url + 'channel/details/v2', params={'token': token, 'channel_id': channel_id})
    channel_details_data = channel_details.json()

    assert channel_details_data == {
        'name': 'name',
        'is_public': True,
        'owner_members': [
            {
                'u_id': id_num,
                'email': 'yes@yes.com',
                'name_first': 'firstname',
                'name_last': 'lastname',
                'handle_str': 'firstnamelastname',
            }
        ],
        'all_members': [
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
'''
# def test_valid_channel_two_owners

def test_valid_channel_unauthorised(clear_and_register):

    channel_id = clear_and_register['channel_id']

    # get token for 2nd user
    register = requests.post(config.url + 'auth/register/v2', json={'email': "yes2@yes.com", 'password': "aaaaaa", 'name_first': "name", "name_last": "name"})
    register_data = register.json()
    token_2 = register_data["token"]

    channel_details = requests.get(config.url + 'channel/details/v2', params={'token': token_2, 'channel_id': channel_id})
    assert channel_details.status_code == AccessError.code

def test_valid_channel_invalid_token(clear_and_register):
    channel_id = clear_and_register['channel_id']
    channel_details = requests.get(config.url + 'channel/details/v2', params={'token': "", 'channel_id': channel_id})
    assert channel_details.status_code == AccessError.code

def test_invalid_channel_unauthorised_valid_id():
    requests.delete(config.url + 'clear/v1')
    register = requests.post(config.url + 'auth/register/v2', json={'email': "yes@yes.com", 'password': "aaaaaa", 'name_first': "firstname", "name_last": "lastname"})
    register_data = register.json()
    token = register_data['token']

    channel_details = requests.get(config.url + 'channel/details/v2', params={'token': token, 'channel_id': 1})
    assert channel_details.status_code == InputError.code

def test_invalid_channel_invalid_id():
    requests.delete(config.url + 'clear/v1')
    channel_details = requests.get(config.url + 'channel/details/v2', params={'token': 1, 'channel_id': 1})
    assert channel_details.status_code == AccessError.code

import pytest
import requests
from src import config
from src.error import AccessError, InputError

'''
channel_join_v2_test.py: All functions related to testing the channel_invite_v2 function
'''

@pytest.fixture
def channel_join_url():
    '''
    This function returns the url to the channel/join/v2 endpoint
    '''
    return config.url + 'channel/join/v2'

@pytest.fixture
def clear_and_register():
    '''
    This function clears the datastore and registers two users
    '''
    requests.delete(config.url + 'clear/v1')

    auth_register_input1 = {
        'email':'user1@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last': 'Last'
    }
    user1_payload = requests.post(config.url + 'auth/register/v2', json=auth_register_input1).json()

    auth_register_input2 = {
        'email':'user2@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last': 'Last'
    }
    user2_payload = requests.post(config.url + 'auth/register/v2', json=auth_register_input2).json()

    return {
        'user1_token': user1_payload['token'],
        'user1_id': user1_payload['auth_user_id'],
        'user2_token': user2_payload['token'],
        'user2_id': user2_payload['auth_user_id']
        }

def test_join_public(channel_join_url, clear_and_register):
    '''
    Testing the general case of a user joining a public channel
    '''
    creator_token = clear_and_register['user1_token']
    user_token = clear_and_register['user2_token']
    user_id = clear_and_register['user2_id']

    channels_create_input = {
        'token': creator_token,
        'name': 'Channel',
        'is_public': True
    }
    channel_id = requests.post(config.url + 'channels/create/v2',json=channels_create_input).json()['channel_id']
    
    channels_join_input = {
        'token': user_token,
        'channel_id': channel_id,
    }
    r = requests.post(channel_join_url, json=channels_join_input)

    channel_details_input = {
        'token': creator_token,
        'channel_id': channel_id
    }
    channel_members = requests.get(config.url + 'channel/details/v2',params=channel_details_input).json()['all_members']
    channel_members_ids = [user['u_id'] for user in channel_members]

    assert r.status_code == 200 and user_id in channel_members_ids

def test_invalid_token(channel_join_url, clear_and_register):
    '''
    Testing the error case of passing an invalid token
    '''
    valid_user_token = clear_and_register['user1_token']

    channels_create_input = {
        'token': valid_user_token,
        'name': 'Channel',
        'is_public': True
    }
    valid_channel_id = requests.post(config.url + 'channels/create/v2',json=channels_create_input).json()['channel_id']

    # Creating an invalid token (empty string)
    invalid_auth_token = ''

    channels_join_input = {
        'token': invalid_auth_token,
        'channel_id': valid_channel_id
    }
    r = requests.post(channel_join_url, json=channels_join_input)
    
    assert r.status_code == AccessError.code

def test_invalid_channel_id(channel_join_url, clear_and_register):
    '''
    Testing the error case of passing an invalid channel_id
    '''
    valid_user_token = clear_and_register['user1_token']

    channels_create_input = {
        'token': valid_user_token,
        'name': 'Channel',
        'is_public': True
    }
    valid_channel_id = requests.post(config.url + 'channels/create/v2',json=channels_create_input).json()['channel_id']

    # Generating an invalid id that doesn't match existing ids
    invalid_channel_id = valid_channel_id + 1

    channels_join_input = {
        'token': valid_user_token,
        'channel_id': invalid_channel_id
    }
    r = requests.post(channel_join_url, json=channels_join_input)
    
    assert r.status_code == InputError.code

def test_all_ids_invalid(channel_join_url, clear_and_register):
    '''
    Testing the error case of passing an invalid token and channel_id
    '''
    valid_user_token = clear_and_register['user1_token']

    channels_create_input = {
        'token': valid_user_token,
        'name': 'Channel',
        'is_public': True
    }
    valid_channel_id = requests.post(config.url + 'channels/create/v2',json=channels_create_input).json()['channel_id']

    # Creating an invalid token (empty string)
    invalid_auth_token = ''
    # Generating invalid channel id that doesn't match any exising ids
    invalid_channel_id = valid_channel_id + 1

    channels_join_input = {
        'token': invalid_auth_token,
        'channel_id': invalid_channel_id
    }
    r = requests.post(channel_join_url, json=channels_join_input)

    assert r.status_code == AccessError.code

def test_duplicate(channel_join_url, clear_and_register):
    '''
    Testing the error case of a user joining a channel again
    '''
    user_token = clear_and_register['user1_token']

    channels_create_input = {
        'token': user_token,
        'name': 'Channel',
        'is_public': True
    }
    channel_id = requests.post(config.url + 'channels/create/v2',json=channels_create_input).json()['channel_id']

    channels_join_input = {
        'token': user_token,
        'channel_id': channel_id
    }
    r = requests.post(channel_join_url, json=channels_join_input)
    
    assert r.status_code == InputError.code

def test_private_channel_without_global_owner(channel_join_url, clear_and_register):
    '''
    Testing the error case of a non-global owner joining a private channel
    '''
    creator_token = clear_and_register['user1_token']
    user_token = clear_and_register['user2_token']

    channels_create_input = {
        'token': creator_token,
        'name': 'Channel',
        'is_public': False
    }
    private_channel_id = requests.post(config.url + 'channels/create/v2',json=channels_create_input).json()['channel_id']

    channels_join_input = {
        'token': user_token,
        'channel_id': private_channel_id
    }
    r = requests.post(channel_join_url, json=channels_join_input)
    
    assert r.status_code == AccessError.code



def test_private_channel_with_global_owner(channel_join_url, clear_and_register):
    '''
    Testing the general case of a global owner joining a private channel
    '''
    creator_token = clear_and_register['user2_token']
    global_owner_token = clear_and_register['user1_token']
    global_owner_id = clear_and_register['user1_id']

    channels_create_input = {
        'token': creator_token,
        'name': 'Channel',
        'is_public': False
    }
    private_channel_id = requests.post(config.url + 'channels/create/v2',json=channels_create_input).json()['channel_id']

    channels_join_input = {
        'token': global_owner_token,
        'channel_id': private_channel_id
    }
    r = requests.post(channel_join_url, json=channels_join_input)

    channel_details_input = {
        'token': creator_token,
        'channel_id': private_channel_id
    }
    channel_members = requests.get(config.url + 'channel/details/v2',params=channel_details_input).json()['all_members']
    channel_members_ids = [user['u_id'] for user in channel_members]

    assert r.status_code == 200 and global_owner_id in channel_members_ids

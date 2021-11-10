import pytest
import requests
from src import config
from src.error import AccessError, InputError

'''
channel_invite_v2_test.py: All functions related to testing the channel_invite_v2 function
'''

@pytest.fixture
def channel_invites_url():
    '''
    This function returns the url to the channel/invite/v2 endpoint
    '''
    return config.url + 'channel/invite/v2'

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


def test_public_channel_invite(channel_invite_url, clear_and_register):
    '''
    Testing the general case of inviting a user to a public channel
    '''
    auth_user_token = clear_and_register['user1_token']
    invitee_id = clear_and_register['user2_id']
    
    channels_create_input = {
        'token': auth_user_token,
        'name': 'Channel',
        'is_public': True
    }
    public_channel_id = requests.post(config.url + 'channels/create/v2',json=channels_create_input).json()['channel_id']
    
    channels_invite_input = {
        'token': auth_user_token,
        'channel_id': public_channel_id,
        'u_id': invitee_id
    }
    r = requests.post(channel_invite_url, json=channels_invite_input)

    channel_details_input = {
        'token': auth_user_token,
        'channel_id': public_channel_id
    }
    channel_members = requests.get(config.url + 'channel/details/v2',params=channel_details_input).json()['all_members']
    channel_members_ids = [user['u_id'] for user in channel_members]

    assert r.status_code == 200 and invitee_id in channel_members_ids

def test_private_channel_invite(channel_invite_url, clear_and_register):
    '''
    Testing the general case of inviting a user to a private channel
    '''
    auth_user_token = clear_and_register['user1_token']
    invitee_id = clear_and_register['user2_id']

    channels_create_input = {
        'token': auth_user_token,
        'name': 'Channel',
        'is_public': False
    }
    private_channel_id = requests.post(config.url + 'channels/create/v2',json=channels_create_input).json()['channel_id']
    
    channels_invite_input = {
        'token': auth_user_token,
        'channel_id': private_channel_id,
        'u_id': invitee_id
    }
    r = requests.post(channel_invite_url, json=channels_invite_input)

    channel_details_input = {
        'token': auth_user_token,
        'channel_id': private_channel_id
    }
    channel_members = requests.get(config.url + 'channel/details/v2',params=channel_details_input).json()['all_members']
    channel_members_ids = [user['u_id'] for user in channel_members]

    assert r.status_code == 200 and invitee_id in channel_members_ids

def test_invalid_token(channel_invite_url, clear_and_register):
    '''
    Testing the error case of passing an invalid token
    '''
    valid_auth_token = clear_and_register['user1_token']
    valid_invitee_id = clear_and_register['user2_id']

    channels_create_input = {
        'token': valid_auth_token,
        'name': 'Channel',
        'is_public': False
    }
    valid_channel_id = requests.post(config.url + 'channels/create/v2',json=channels_create_input).json()['channel_id']

    # Creating an invalid token (empty string)
    invalid_auth_token = ''

    channels_invite_input = {
        'token': invalid_auth_token,
        'channel_id': valid_channel_id,
        'u_id': valid_invitee_id
    }
    r = requests.post(channel_invite_url, json=channels_invite_input)
    
    assert r.status_code == AccessError.code

def test_invalid_invitee_id(channel_invite_url, clear_and_register):
    '''
    Testing the error case of passing an invalid u_id
    '''
    valid_auth_token = clear_and_register['user1_token']
    valid_auth_id = clear_and_register['user1_id']
    valid_invitee_id = clear_and_register['user2_id']

    channels_create_input = {
        'token': valid_auth_token,
        'name': 'Channel',
        'is_public': False
    }
    valid_channel_id = requests.post(config.url + 'channels/create/v2',json=channels_create_input).json()['channel_id']

    # Generating an invalid id that does not match the two previously created ids.
    invalid_invitee_id = valid_invitee_id + 1
    if invalid_invitee_id == valid_auth_id:
        invalid_invitee_id += 1

    channels_invite_input = {
        'token': valid_auth_token,
        'channel_id': valid_channel_id,
        'u_id': invalid_invitee_id
    }
    r = requests.post(channel_invite_url, json=channels_invite_input)
    
    assert r.status_code == InputError.code

def test_invalid_channel_id(channel_invite_url, clear_and_register):
    '''
    Testing the error case of passing an invalid channel_id
    '''
    valid_auth_token = clear_and_register['user1_token']
    valid_invitee_id = clear_and_register['user2_id']

    channels_create_input = {
        'token': valid_auth_token,
        'name': 'Channel',
        'is_public': True
    }
    valid_channel_id = requests.post(config.url + 'channels/create/v2',json=channels_create_input).json()['channel_id']

    # Generating an invalid id that does not match the previously created id.
    invalid_channel_id = valid_channel_id + 1

    channels_invite_input = {
        'token': valid_auth_token,
        'channel_id': invalid_channel_id,
        'u_id': valid_invitee_id
    }
    r = requests.post(channel_invite_url, json=channels_invite_input)

    assert r.status_code == InputError.code

def test_all_ids_invalid(channel_invite_url, clear_and_register):
    '''
    Testing the error case of passing an invalid token, channel_id and u_id
    '''
    valid_auth_token = clear_and_register['user1_token']
    valid_auth_id = clear_and_register['user1_id']
    valid_invitee_id = clear_and_register['user2_id']

    channels_create_input = {
        'token': valid_auth_token,
        'name': 'Channel',
        'is_public': False
    }
    valid_channel_id = requests.post(config.url + 'channels/create/v2',json=channels_create_input).json()['channel_id']

    # Generating an invalid id that does not match the previously created channel id.
    invalid_channel_id = valid_channel_id + 1

    # Creating an invalid token (empty string)
    invalid_auth_token = ''

    # Generating an invalid id that does not match the three previous user ids.
    invalid_invitee_id = valid_invitee_id + 1
    if invalid_invitee_id == valid_auth_id:
        invalid_invitee_id += 1

    channels_invite_input = {
        'token': invalid_auth_token,
        'channel_id': invalid_channel_id,
        'u_id': invalid_invitee_id
    }
    r = requests.post(channel_invite_url, json=channels_invite_input)

    assert r.status_code == AccessError.code

def test_duplicate_invite(channel_invite_url, clear_and_register):
    '''
    Testing the error case of inviting a user to a channel twice
    '''
    auth_token = clear_and_register['user1_token']
    invitee_id = clear_and_register['user2_id']

    channels_create_input = {
        'token': auth_token,
        'name': 'Channel',
        'is_public': False
    }
    channel_id = requests.post(config.url + 'channels/create/v2',json=channels_create_input).json()['channel_id']

    channels_invite_input = {
        'token': auth_token,
        'channel_id': channel_id,
        'u_id': invitee_id
    }
    r = requests.post(channel_invite_url, json=channels_invite_input)
    r = requests.post(channel_invite_url, json=channels_invite_input)
    
    assert r.status_code == InputError.code

def test_inviter_not_in_channel(channel_invite_url, clear_and_register):
    '''
    Testing the error case of inviting a user to a channel that the inviter is not a member of
    '''
    owner_token = clear_and_register['user1_token']
    inviter_token = clear_and_register['user2_token']

    channels_create_input = {
        'token': owner_token,
        'name': 'Channel',
        'is_public': False
    }
    channel_id = requests.post(config.url + 'channels/create/v2',json=channels_create_input).json()['channel_id']

    auth_register_input = {
        'email':'user3@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last': 'Last'
    }
    invitee_id = requests.post(config.url + 'auth/register/v2', json=auth_register_input).json()['auth_user_id']

    channels_invite_input = {
        'token': inviter_token,
        'channel_id': channel_id,
        'u_id': invitee_id
    }
    r = requests.post(channel_invite_url, json=channels_invite_input)

    assert r.status_code == AccessError.code


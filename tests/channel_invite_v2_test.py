import pytest
import requests
import json
from src import config


@pytest.fixture
def channel_invite_url():
    return config.url + 'channel/invite/v2'

@pytest.fixture
def clear_and_register():
    requests.delete(config.url + 'clear/v1')

    user1_input = {
        'email':'user1@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last': 'Last'
    }
    user1_dict = requests.post(config.url + 'auth/register/v2', json=user1_input).json()
    
    user2_input = {
        'email':'user2@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last': 'Last'
    }
    user2_dict = requests.post(config.url + 'auth/register/v2', json=user2_input).json()
    
    return {'user1_id': user1_dict['auth_user_id'], 'user2_id': user2_dict['auth_user_id']}

# Testing the general case of inviting a user to a public channel
def test_public_channel_invite(channel_invite_url, clear_and_register):
    auth_id = clear_and_register['user1_id']
    invitee_id = clear_and_register['user2_id']
    channels_create_input = {
        'token': str(auth_id),
        'name': 'Channel',
        'is_public': True
    }
    public_channel_id = requests.post(config.url + 'channels/create/v2',json=channels_create_input).json()['channel_id']
    
    channels_invite_input = {
        'token': str(auth_id),
        'channel_id': public_channel_id,
        'u_id': invitee_id
    }
    requests.post(channel_invite_url, json=channels_invite_input)

    channel_details_input = {
        'token': str(auth_id),
        'channel_id': public_channel_id
    }
    channel_members = requests.get(config.url + 'channel/details/v2',params=channel_details_input).json()['all_members']
    channel_members_ids = [user['u_id'] for user in channel_members]

    assert invitee_id in channel_members_ids

# Testing the general case of inviting a user to a private channel
def test_private_channel_invite(channel_invite_url, clear_and_register):
    auth_id = clear_and_register['user1_id']
    invitee_id = clear_and_register['user2_id']
    channels_create_input = {
        'token': str(auth_id),
        'name': 'Channel',
        'is_public': False
    }
    private_channel_id = requests.post(config.url + 'channels/create/v2',json=channels_create_input).json()['channel_id']
    
    channels_invite_input = {
        'token': str(auth_id),
        'channel_id': private_channel_id,
        'u_id': invitee_id
    }
    requests.post(channel_invite_url, json=channels_invite_input)

    channel_details_input = {
        'token': str(auth_id),
        'channel_id': private_channel_id
    }
    channel_members = requests.get(config.url + 'channel/details/v2',params=channel_details_input).json()['all_members']
    channel_members_ids = [user['u_id'] for user in channel_members]

    assert invitee_id in channel_members_ids

# Testing the error case of passing an invalid auth_user_id
def test_invalid_auth_id(channel_invite_url, clear_and_register):
    valid_auth_id = clear_and_register['user1_id']
    valid_invitee_id = clear_and_register['user2_id']
    channels_create_input = {
        'token': str(valid_auth_id),
        'name': 'Channel',
        'is_public': False
    }
    valid_channel_id = requests.post(config.url + 'channels/create/v2',json=channels_create_input).json()['channel_id']

    # Generating an invalid id that does not match the two previously created ids.
    invalid_auth_id = valid_auth_id + 1
    if invalid_auth_id == valid_invitee_id:
        invalid_auth_id += 1

    channels_invite_input = {
        'token': str(invalid_auth_id),
        'channel_id': valid_channel_id,
        'u_id': valid_invitee_id
    }
    r = requests.post(channel_invite_url, json=channels_invite_input)
    
    #Throws AccessError
    assert r.status_code == 403

# Testing the error case of passing an invalid u_id
def test_invalid_invitee_id(channel_invite_url, clear_and_register):
    valid_auth_id = clear_and_register['user1_id']
    valid_invitee_id = clear_and_register['user2_id']
    channels_create_input = {
        'token': str(valid_auth_id),
        'name': 'Channel',
        'is_public': False
    }
    valid_channel_id = requests.post(config.url + 'channels/create/v2',json=channels_create_input).json()['channel_id']

    # Generating an invalid id that does not match the two previously created ids.
    invalid_invitee_id = valid_invitee_id + 1
    if invalid_invitee_id == valid_auth_id:
        invalid_invitee_id += 1

    channels_invite_input = {
        'token': str(valid_auth_id),
        'channel_id': valid_channel_id,
        'u_id': invalid_invitee_id
    }
    r = requests.post(channel_invite_url, json=channels_invite_input)
    
    #Throws InputError
    assert r.status_code == 400

# Testing the error case of passing an invalid channel_id
def test_invalid_channel_id(channel_invite_url, clear_and_register):
    valid_auth_id = clear_and_register['user1_id']
    valid_invitee_id = clear_and_register['user2_id']

    channels_create_input = {
        'token': str(valid_auth_id),
        'name': 'Channel',
        'is_public': True
    }
    valid_channel_id = requests.post(config.url + 'channels/create/v2',json=channels_create_input).json()['channel_id']

    # Generating an invalid id that does not match the previously created id.
    invalid_channel_id = valid_channel_id + 1

    channels_invite_input = {
        'token': str(valid_auth_id),
        'channel_id': invalid_channel_id,
        'u_id': valid_invitee_id
    }
    r = requests.post(channel_invite_url, json=channels_invite_input)

    #Throws InputError
    assert r.status_code == 400

# Testing the error case of passing an invalid auth_user_id, channel_id and u_id
def test_all_ids_invalid(channel_invite_url, clear_and_register):
    valid_auth_id = clear_and_register['user1_id']
    valid_invitee_id = clear_and_register['user2_id']

    channels_create_input = {
        'token': str(valid_auth_id),
        'name': 'Channel',
        'is_public': False
    }
    valid_channel_id = requests.post(config.url + 'channels/create/v2',json=channels_create_input).json()['channel_id']

    # Generating an invalid id that does not match the previously created channel id.
    invalid_channel_id = valid_channel_id + 1

    # Generating an invalid id that does not match the two previously created user ids.
    invalid_auth_id = valid_auth_id + 1
    if invalid_auth_id == valid_invitee_id:
        invalid_auth_id += 1

    # Generating an invalid id that does not match the three previous user ids.
    invalid_invitee_id = valid_invitee_id + 1
    while (invalid_invitee_id == valid_auth_id) or (invalid_invitee_id == invalid_auth_id):
        invalid_invitee_id += 1

    channels_invite_input = {
        'token': str(invalid_auth_id),
        'channel_id': invalid_channel_id,
        'u_id': invalid_invitee_id
    }
    r = requests.post(channel_invite_url, json=channels_invite_input)

    #Throws AccessError
    assert r.status_code == 403

# Testing the error case of inviting a user to a channel twice
def test_duplicate_invite(channel_invite_url, clear_and_register):
    auth_id = clear_and_register['user1_id']
    invitee_id = clear_and_register['user2_id']

    channels_create_input = {
        'token': str(auth_id),
        'name': 'Channel',
        'is_public': False
    }
    channel_id = requests.post(config.url + 'channels/create/v2',json=channels_create_input).json()['channel_id']

    channels_invite_input = {
        'token': str(auth_id),
        'channel_id': channel_id,
        'u_id': invitee_id
    }
    requests.post(channel_invite_url, json=channels_invite_input)
    r = requests.post(channel_invite_url, json=channels_invite_input)
    
    #Throws InputError
    assert r.status_code == 400

# Testing the error case of inviting a user to a channel that the inviter is not a member of
def test_inviter_not_in_channel(channel_invite_url, clear_and_register):
    auth_id = clear_and_register['user1_id']
    inviter_id = clear_and_register['user2_id']
    channels_create_input = {
        'token': str(auth_id),
        'name': 'Channel',
        'is_public': False
    }
    channel_id = requests.post(config.url + 'channels/create/v2',json=channels_create_input).json()['channel_id']

    auth_register_input = {
        'email':'user@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last': 'Last'
    }
    invitee_id = requests.post(config.url + 'auth/register/v2', json=auth_register_input).json()['auth_user_id']

    channels_invite_input = {
        'token': str(inviter_id),
        'channel_id': channel_id,
        'u_id': invitee_id
    }
    r = requests.post(channel_invite_url, json=channels_invite_input)

    #Throws AccessError
    assert r.status_code == 403


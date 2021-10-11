import pytest
import requests
import json
from src import config


@pytest.fixture
def channel_join_url():
    return config.url + 'channel/join/v2'

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

# Testing the general case of a user joining a public channel
def test_general(channel_join_url, clear_and_register):
    creator_id = clear_and_register['user1_id']
    user_id = clear_and_register['user2_id']
    channels_create_input = {
        'token': str(creator_id),
        'name': 'Channel',
        'is_public': True
    }
    channel_id = requests.post(config.url + 'channels/create/v2',json=channels_create_input).json()['channel_id']
    
    channels_join_input = {
        'token': str(user_id),
        'channel_id': channel_id,
    }
    requests.post(channel_join_url, json=channels_join_input)

    channel_details_input = {
        'token': str(creator_id),
        'channel_id': channel_id
    }
    channel_members = requests.get(config.url + 'channel/details/v2',params=channel_details_input).json()['all_members']
    channel_members_ids = [user['u_id'] for user in channel_members]

    assert user_id in channel_members_ids

# Testing the error case of passing an invalid auth_user_id
def test_invalid_user_id(channel_join_url, clear_and_register):
    valid_user_id = clear_and_register['user1_id']
    channels_create_input = {
        'token': str(valid_user_id),
        'name': 'Channel',
        'is_public': True
    }
    valid_channel_id = requests.post(config.url + 'channels/create/v2',json=channels_create_input).json()['channel_id']

    # Generating an invalid id that doesn't match existing ids
    invalid_user_id = valid_user_id + 1
    if invalid_user_id == clear_and_register['user2_id']:
        invalid_user_id += 1

    channels_join_input = {
        'token': str(invalid_user_id),
        'channel_id': valid_channel_id
    }
    r = requests.post(channel_join_url, json=channels_join_input)
    
    #Throws AccessError
    assert r.status_code == 403

# Testing the error case of passing an invalid channel_id
def test_invalid_channel_id(channel_join_url, clear_and_register):
    valid_user_id = clear_and_register['user1_id']
    channels_create_input = {
        'token': str(valid_user_id),
        'name': 'Channel',
        'is_public': True
    }
    valid_channel_id = requests.post(config.url + 'channels/create/v2',json=channels_create_input).json()['channel_id']

    # Generating an invalid id that doesn't match existing ids
    invalid_channel_id = valid_channel_id + 1

    channels_join_input = {
        'token': str(valid_user_id),
        'channel_id': invalid_channel_id
    }
    r = requests.post(channel_join_url, json=channels_join_input)
    
    #Throws InputError
    assert r.status_code == 400

# Testing the error case of passing an invalid auth_user_id and channel_id
def test_all_ids_invalid(channel_join_url, clear_and_register):
    valid_user_id = clear_and_register['user1_id']

    channels_create_input = {
        'token': str(valid_user_id),
        'name': 'Channel',
        'is_public': True
    }
    valid_channel_id = requests.post(config.url + 'channels/create/v2',json=channels_create_input).json()['channel_id']

    # Generating invalid ids that don't match exising ids
    invalid_channel_id = valid_channel_id + 1
    invalid_user_id = valid_user_id + 1
    if invalid_user_id == clear_and_register['user2_id']:
        invalid_user_id += 1

    channels_join_input = {
        'token': str(invalid_user_id),
        'channel_id': invalid_channel_id
    }
    r = requests.post(channel_join_url, json=channels_join_input)

    #Throws AccessError
    assert r.status_code == 403

# Testing the error case of a user joining a channel again
def test_duplicate(channel_join_url, clear_and_register):
    user_id = clear_and_register['user1_id']

    channels_create_input = {
        'token': str(user_id),
        'name': 'Channel',
        'is_public': True
    }
    channel_id = requests.post(config.url + 'channels/create/v2',json=channels_create_input).json()['channel_id']

    channels_join_input = {
        'token': str(user_id),
        'channel_id': channel_id
    }
    r = requests.post(channel_join_url, json=channels_join_input)
    
    #Throws InputError
    assert r.status_code == 400

# Testing the error case of a non-global owner joining a private channel
def test_private_channel_without_global_owner(clear_and_register):
    creator_id = clear_and_register['user1_id']
    user_id = clear_and_register['user2_id']
    channels_create_input = {
        'token': str(creator_id),
        'name': 'Channel',
        'is_public': False
    }
    private_channel_id = requests.post(config.url + 'channels/create/v2',json=channels_create_input).json()['channel_id']

    channels_join_input = {
        'token': str(user_id),
        'channel_id': private_channel_id
    }
    r = requests.post(channel_join_url, json=channels_join_input)
    
    #Throws AccessError
    assert r.status_code == 403



# Testing the general case of a global owner joining a private channel
def test_private_channel_with_global_owner(clear_and_register):
    global_owner_id = clear_and_register['user1_id']
    creator_id = clear_and_register['user2_id']
    channels_create_input = {
        'token': str(creator_id),
        'name': 'Channel',
        'is_public': False
    }
    private_channel_id = requests.post(config.url + 'channels/create/v2',json=channels_create_input).json()['channel_id']

    channels_join_input = {
        'token': str(global_owner_id),
        'channel_id': private_channel_id
    }
    requests.post(channel_join_url, json=channels_join_input)

    channel_details_input = {
        'token': str(creator_id),
        'channel_id': private_channel_id
    }
    channel_members = requests.get(config.url + 'channel/details/v2',params=channel_details_input).json()['all_members']
    channel_members_ids = [user['u_id'] for user in channel_members]

    assert global_owner_id in channel_members_ids

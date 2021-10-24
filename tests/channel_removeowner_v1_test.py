import pytest
import requests
import json
from src import config
from src.error import AccessError, InputError

@pytest.fixture
def clear_and_channel_2_members():
    
    requests.delete(config.url + 'clear/v1')
    register = requests.post(config.url + 'auth/register/v2', json={
        'email': "yes@yes.com", 
        'password': "aaaaaa", 
        'name_first': "firstname", 
        "name_last": "lastname"
    })
    register_data = register.json()
    token = register_data['token']

    channel_create = requests.post(config.url + 'channels/create/v2', json={
        'token': token, 
        'name': 'name', 
        'is_public': True
    })
    channel_create_data = channel_create.json()
    channel_id = channel_create_data['channel_id']

    register_2 = requests.post(config.url + 'auth/register/v2', json={
        'email': "yes2@yes.com", 
        'password': "aaaaaa", 
        'name_first': "name", 
        "name_last": "name"
    })
    register_2_data = register_2.json()
    u_id_2 = register_2_data['auth_user_id']

    requests.post(config.url + 'channel/invite/v2', json={'token': token, 'channel_id': channel_id, 'u_id': u_id_2})
    

    return {
        'token': token, 
        'token_2': register_2_data['token'], 
        'u_id': register_data['auth_user_id'], 
        'u_id_2': u_id_2, 
        'channel_id': channel_id
        }

# when valid token, valid channel, removes a channel owner 
def test_valid_channel_remove_channel_owner(clear_and_channel_2_members):
    token = clear_and_channel_2_members['token']
    u_id = clear_and_channel_2_members['u_id']
    u_id_2 = clear_and_channel_2_members['u_id_2']
    channel_id = clear_and_channel_2_members['channel_id']

    requests.post(config.url + 'channel/addowner/v1', json={
        'token': token, 
        'channel_id': channel_id, 
        'u_id': u_id_2
    })
    requests.post(config.url + 'channel/removeowner/v1', json={
        'token': token, 
        'channel_id': channel_id, 
        'u_id': u_id_2
    })

    channel_details = requests.get(config.url + 'channel/details/v2', params={'token': token, 'channel_id': channel_id})
    channel_details_data = channel_details.json()
    assert channel_details_data['owner_members'] == [
            {
                'u_id': u_id,
                'email': 'yes@yes.com',
                'name_first': 'firstname',
                'name_last': 'lastname',
                'handle_str': 'firstnamelastname',
            } ,
        ]

# valid token, invalid channel
def test_invalid_channel():
    requests.delete(config.url + 'clear/v1')
    register = requests.post(config.url + 'auth/register/v2', json={
        'email': "yes@yes.com", 
        'password': "aaaaaa", 
        'name_first': "firstname", 
        "name_last": "lastname"
    })
    register_data = register.json()
    token = register_data['token']
    u_id = register_data['auth_user_id']
    channel_removeowner = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': token, 
        'channel_id': 1, 
        'u_id': u_id
    })
    assert channel_removeowner.status_code == InputError.code

# valid token, valid channel, invalid u_id
def test_invalid_u_id(clear_and_channel_2_members):
    token = clear_and_channel_2_members['token']
    u_id = clear_and_channel_2_members['u_id']
    u_id_2 = clear_and_channel_2_members['u_id_2']
    channel_id = clear_and_channel_2_members['channel_id']

    invalid_u_id = 1
    while (invalid_u_id == u_id or invalid_u_id == u_id_2):
        invalid_u_id += 1
    channel_removeowner = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': token, 
        'channel_id': channel_id, 
        'u_id': invalid_u_id
    })
    assert channel_removeowner.status_code == InputError.code


# valid token, valid channel, not an owner
def test_not_channel_owner(clear_and_channel_2_members):
    token = clear_and_channel_2_members['token']
    u_id_2 = clear_and_channel_2_members['u_id_2']
    channel_id = clear_and_channel_2_members['channel_id']

    channel_removeowner = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': token, 
        'channel_id': channel_id, 
        'u_id': u_id_2
    })
    assert channel_removeowner.status_code == InputError.code

# valid token, valid channel, only owner
def test_only_channel_owner(clear_and_channel_2_members):
    token = clear_and_channel_2_members['token']
    u_id = clear_and_channel_2_members['u_id']
    channel_id = clear_and_channel_2_members['channel_id']

    channel_removeowner = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': token, 
        'channel_id': channel_id, 
        'u_id': u_id
    })
    assert channel_removeowner.status_code == InputError.code

# valid token, valid channel, no owner permissions
def test_no_owner_permissions(clear_and_channel_2_members):
    token_2 = clear_and_channel_2_members['token_2']
    u_id = clear_and_channel_2_members['u_id']
    channel_id = clear_and_channel_2_members['channel_id']

    channel_removeowner = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': token_2, 
        'channel_id': channel_id, 
        'u_id': u_id
    })
    assert channel_removeowner.status_code == AccessError.code

# invalid token, valid channel
def test_invalid_token_valid_channel(clear_and_channel_2_members):
    token = clear_and_channel_2_members['token']
    token_2 = clear_and_channel_2_members['token_2']
    u_id_2 = clear_and_channel_2_members['u_id_2']
    channel_id = clear_and_channel_2_members['channel_id']

    invalid_token = 1
    while (invalid_token == token or invalid_token == token_2):
        invalid_token += 1

    requests.post(config.url + 'channel/addowner/v1', json={
        'token': token, 
        'channel_id': channel_id, 
        'u_id': u_id_2
    })
    channel_removeowner = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': invalid_token, 
        'channel_id': channel_id, 
        'u_id': u_id_2
    })
    assert channel_removeowner.status_code == AccessError.code

# invalid token , invalid channel
def test_invalid_token_invalid_channel(clear_and_channel_2_members):
    token = clear_and_channel_2_members['token']
    token_2 = clear_and_channel_2_members['token_2']
    u_id_2 = clear_and_channel_2_members['u_id_2']
    channel_id = clear_and_channel_2_members['channel_id']

    invalid_token = 1
    while (invalid_token == token or invalid_token == token_2):
        invalid_token += 1
    
    invalid_channel_id = 1
    while (invalid_channel_id == channel_id):
        invalid_channel_id += 1

    requests.post(config.url + 'channel/addowner/v1', json={
        'token': token, 
        'channel_id': channel_id, 
        'u_id': u_id_2
    })
    channel_removeowner = requests.post(config.url + 'channel/removeowner/v1', json={
        'token': invalid_token, 
        'channel_id': invalid_channel_id, 
        'u_id': u_id_2
    })
    assert channel_removeowner.status_code == AccessError.code

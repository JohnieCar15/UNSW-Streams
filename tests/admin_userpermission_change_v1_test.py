import pytest
import requests
from src import config
from src.error import AccessError, InputError

@pytest.fixture
def admin_userpermission_change_url():
    return config.url + 'admin/userpermission/change/v1'

@pytest.fixture
def clear_and_register():
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

# Testing the general case of changing an owner to a member
def test_change_to_member(admin_userpermission_change_url, clear_and_register):
    owner_token = clear_and_register['user1_token']
    owner_id = clear_and_register['user1_id']
    new_owner_token = clear_and_register['user1_token']
    new_owner_id = clear_and_register['user2_id']
    
    # Changing the second user to an owner
    requests.post(admin_userpermission_change_url, json={
        'token': owner_token,
        'u_id': new_owner_id,
        'permission_id': 1
    })


    # Demoting the first owner to a member
    admin_userpermission_change_input = {
        'token': new_owner_token,
        'u_id': owner_id,
        'permission_id': 2
    }
    r = requests.post(admin_userpermission_change_url, json=admin_userpermission_change_input)

    # Testing successful permission change by seeing if the user can no longer join a private channel
    channel_id = requests.post(config.url + 'channels/create/v2', json={
        'token': new_owner_token,
        'name': 'Channel',
        'is_public': False
    }).json()['channel_id']

    channel_join_status_code = requests.post(config.url + 'channel/join/v2', json={
        'token': owner_token,
        'channel_id': channel_id
    }).status_code

    assert r.status_code == 200 and channel_join_status_code == AccessError.code

# Testing the general case of changing an member to a owner
def test_change_to_owner(admin_userpermission_change_url, clear_and_register):
    auth_user_token = clear_and_register['user1_token']
    user_token = clear_and_register['user2_token']
    user_id = clear_and_register['user2_id']

    admin_userpermission_change_input = {
        'token': auth_user_token,
        'u_id': user_id,
        'permission_id': 1
    }
    r = requests.post(admin_userpermission_change_url, json=admin_userpermission_change_input)

    # Testing successful permission change by seeing if the user can join a private channel
    channel_id = requests.post(config.url + 'channels/create/v2', json={
        'token': auth_user_token,
        'name': 'Channel',
        'is_public': False
    }).json()['channel_id']

    channel_join_status_code = requests.post(config.url + 'channel/join/v2', json={
        'token': user_token,
        'channel_id': channel_id
    }).status_code
    

    assert r.status_code == 200 and channel_join_status_code == 200

# Testing the error case of passing in an invalid token
def test_invalid_token(admin_userpermission_change_url, clear_and_register):
    user_id = clear_and_register['user2_id']

    # Creating an invalid token (empty string)
    invalid_auth_token = ''

    admin_userpermission_change_input = {
        'token': invalid_auth_token,
        'u_id': user_id,
        'permission_id': 1
    }
    r = requests.post(admin_userpermission_change_url, json=admin_userpermission_change_input)

    assert r.status_code == AccessError.code

# Testing the error case of passing in an invalid u_id
def test_invalid_u_id(admin_userpermission_change_url, clear_and_register):
    auth_user_token = clear_and_register['user1_token']
    auth_user_id = clear_and_register['user1_id']
    valid_user_id = clear_and_register['user2_id']

    # Finding an invalid user_id that does not match any existing ids
    invalid_user_id = valid_user_id + 1
    if invalid_user_id == auth_user_id:
        invalid_user_id += 1

    admin_userpermission_change_input = {
        'token': auth_user_token,
        'u_id': invalid_user_id,
        'permission_id': 1
    }
    r = requests.post(admin_userpermission_change_url, json=admin_userpermission_change_input)

    assert r.status_code == InputError.code

# Testing the error case of passing in an invalid permission_id
def test_invalid_permission_id(admin_userpermission_change_url, clear_and_register):
    auth_user_token = clear_and_register['user1_token']
    user_id = clear_and_register['user2_id']

    # Passing in an invalid permission_id of 3
    admin_userpermission_change_input = {
        'token': auth_user_token,
        'u_id': user_id,
        'permission_id': 3
    }
    r = requests.post(admin_userpermission_change_url, json=admin_userpermission_change_input)

    assert r.status_code == InputError.code

# Testing the error case of when the auth_user is not a global owner
def test_auth_not_global_owner(admin_userpermission_change_url, clear_and_register):
    non_global_owner_token = clear_and_register['user2_token']
    non_global_owner_id = clear_and_register['user2_id']

    admin_userpermission_change_input = {
        'token': non_global_owner_token,
        'u_id': non_global_owner_id,
        'permission_id': 1
    }
    r = requests.post(admin_userpermission_change_url, json=admin_userpermission_change_input)

    assert r.status_code == AccessError.code

# Testing the error case of when the demoted user is the only global owner
def test_demoting_only_global_owner(admin_userpermission_change_url, clear_and_register):
    global_owner_token = clear_and_register['user1_token']
    global_owner_id = clear_and_register['user1_id']

    admin_userpermission_change_input = {
        'token': global_owner_token,
        'u_id': global_owner_id,
        'permission_id': 2
    }
    r = requests.post(admin_userpermission_change_url, json=admin_userpermission_change_input)

    assert r.status_code == InputError.code

# Testing the error case of when the auth_user_id, u_id and permission_id are invalid
def test_all_invalid_inputs(admin_userpermission_change_url, clear_and_register):
    non_global_auth_token = clear_and_register['user2_token']
    non_global_auth_id = clear_and_register['user2_id']
    valid_user_id = clear_and_register['user1_id']

    # Finding an invalid user_id that does not match any existing ids
    invalid_user_id = valid_user_id + 1
    if invalid_user_id == non_global_auth_id:
        invalid_user_id += 1

    admin_userpermission_change_input = {
        'token': non_global_auth_token,
        'u_id': invalid_user_id,
        'permission_id': 3
    }
    r = requests.post(admin_userpermission_change_url, json=admin_userpermission_change_input)

    assert r.status_code == AccessError.code

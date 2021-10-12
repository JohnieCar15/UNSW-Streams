import pytest
import requests
from src import config
from src.error import AccessError, InputError

@pytest.fixture
def admin_user_remove_url():
    return config.url + 'admin/user/remove/v1'

@pytest.fixture
def clear_and_register():
    requests.delete(config.url + 'clear/v1')

    auth_register_input1 = {
        'email':'user1@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last': 'Last'
    }
    user1_id = requests.post(config.url + 'auth/register/v2', json=auth_register_input1).json()['auth_user_id']

    auth_register_input2 = {
        'email':'user2@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last': 'Last'
    }
    user2_id = requests.post(config.url + 'auth/register/v2', json=auth_register_input2).json()['auth_user_id']

    return {'user1_id': user1_id, 'user2_id': user2_id}

# Testing the general case of removing a user from Streams
def test_remove_user(admin_user_remove_url, clear_and_register):
    auth_id = clear_and_register['user1_id']
    user_id = clear_and_register['user2_id']

    dm_id = requests.post(config.url + 'dm/create/v1', json={
        'token': str(auth_id),
        'u_ids': []
    }).json()['dm_id']
    channel_id = requests.post(config.url + 'channels/create/v2', json={
        'token': str(auth_id),
        'name': 'Channel',
        'is_public': True
    }).json()['channel_id']


    admin_user_remove_input = {
        'token': str(auth_id),
        'u_id': user_id
    }
    r = requests.delete(admin_user_remove_url, json=admin_user_remove_input)


    dm_members = requests.get(config.url + 'dm/details/v1', params={
        'token': str(auth_id),
        'dm_id': dm_id
    }).json()['members']
    dm_members_ids = [user['u_id'] for user in dm_members]

    
    channel_members = requests.get(config.url + 'channel/details/v1', params={
        'token': str(auth_id),
        'channel_id': channel_id
    }).json()['all_members']
    channel_members_ids = [user['u_id'] for user in channel_members]

    all_users_list = requests.get(config.url + 'users/all/v1', params={'token': str(auth_id)}).json()['users']
    all_users_id_list = [user['user_id'] for user in all_users_list]

    user_info = requests.get(config.url + 'user/profile/v1', params={'token': str(auth_id), 'u_id':user_id}).json()
    

    assert r.status_code == 200
    assert user_id not in dm_members_ids
    assert user_id not in channel_members_ids
    assert user_id not in all_users_id_list
    assert user_info['name_first'] == 'Removed' and user_info['name_last'] == 'user'

# Testing the error case of passing in an invalid token
def test_invalid_token(admin_user_remove_url, clear_and_register):
    valid_auth_id = clear_and_register['user1_id']
    user_id = clear_and_register['user2_id']

    # Finding an invalid auth_user_id that does not match any existing ids
    invalid_auth_id = valid_auth_id + 1
    if invalid_auth_id == user_id:
        invalid_auth_id += 1

    admin_user_remove_input = {
        'token': str(invalid_auth_id),
        'u_id': user_id
    }
    r = requests.delete(admin_user_remove_url, json=admin_user_remove_input)

    # Throws AccessError
    assert r.status_code == AccessError.code

# Testing the error case of passing in an invalid u_id
def test_invalid_u_id(admin_user_remove_url, clear_and_register):
    auth_user_id = clear_and_register['user1_id']
    valid_user_id = clear_and_register['user2_id']

    # Finding an invalid user_id that does not match any existing ids
    invalid_user_id = valid_user_id + 1
    if invalid_user_id == auth_user_id:
        invalid_user_id += 1

    admin_user_remove_input = {
        'token': str(auth_user_id),
        'u_id': invalid_user_id
    }
    r = requests.delete(admin_user_remove_url, json=admin_user_remove_input)

    # Throws InputError
    assert r.status_code == InputError.code

# Testing the error case of when the auth_user is not a global owner
def test_auth_not_global_owner(admin_user_remove_url, clear_and_register):
    non_global_owner_id = clear_and_register['user2_id']

    admin_user_remove_input = {
        'token': str(non_global_owner_id),
        'u_id': non_global_owner_id
    }
    r = requests.delete(admin_user_remove_url, json=admin_user_remove_input)

    # Throws AccessError
    assert r.status_code == AccessError.code

# Testing the error case of when the removed user is the only global owner
def test_user_only_global_owner(admin_user_remove_url, clear_and_register):
    global_owner_id = clear_and_register['user1_id']

    admin_user_remove_input = {
        'token': str(global_owner_id),
        'u_id': global_owner_id
    }
    r = requests.delete(admin_user_remove_url, json=admin_user_remove_input)

    # Throws InputError
    assert r.status_code == InputError.code

# Testing the error case of when both the auth_user_id and u_id are invalid
def test_invalid_auth_id_and_u_id(admin_user_remove_url, clear_and_register):
    # Throws AccessError
    assert r.status_code == AccessError.code

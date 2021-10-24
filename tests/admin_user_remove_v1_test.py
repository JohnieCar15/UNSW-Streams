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

# Testing the general case of removing a user from Streams
def test_remove_user(admin_user_remove_url, clear_and_register):
    auth_user_token = clear_and_register['user1_token']
    user_id = clear_and_register['user2_id']
    user_token = clear_and_register['user2_token']

    # Getting the email and handle of the user before removing them
    removed_user_info = requests.get(config.url + 'user/profile/v1', params={'token': auth_user_token, 'u_id':user_id}).json()
    removed_user_email = removed_user_info['user']['email']
    removed_user_handle = removed_user_info['user']['handle_str']

    # Creating a new dm to test admin_user_remove success
    dm_id = requests.post(config.url + 'dm/create/v1', json={
        'token': auth_user_token,
        'u_ids': [user_id]
    }).json()['dm_id']

    # Creating a new channel to test admin_user_remove success
    channel_id = requests.post(config.url + 'channels/create/v2', json={
        'token': auth_user_token,
        'name': 'Channel',
        'is_public': True
    }).json()['channel_id']
    requests.post(config.url + 'channel/join/v2', json={
        'token': user_token,
        'channel_id': channel_id,
    })
    requests.post(config.url + 'channel/addowner/v1', json={
        'token': auth_user_token,
        'channel_id': channel_id,
        'u_id': user_id
    })


    #Sending a message in both the channel and dm to check if later removed
    requests.post(config.url + 'message/senddm/v1', json={
        'token': auth_user_token,
        'dm_id': dm_id,
        'message': 'existing message'
    })
    requests.post(config.url + 'message/senddm/v1', json={
        'token': user_token,
        'dm_id': dm_id,
        'message': 'message'
    })
    requests.post(config.url + 'message/send/v1', json={
        'token': user_token,
        'channel_id': channel_id,
        'message': 'message'
    })

    # Removing the user from Streams
    admin_user_remove_input = {
        'token': auth_user_token,
        'u_id': user_id
    }
    r = requests.delete(admin_user_remove_url, json=admin_user_remove_input)


    # Getting list of messages from the channel and dm sent by the removed user
    channel_messages = requests.get(config.url + 'channel/messages/v2', params={
        'token': auth_user_token,
        'channel_id': channel_id,
        'start': 0
    }).json()['messages']
    removed_user_messages = [message['message'] for message in channel_messages if message['u_id'] == user_id]
    
    dm_messages = requests.get(config.url + 'dm/messages/v1', params={
        'token': auth_user_token,
        'dm_id': dm_id,
        'start': 0
    }).json()['messages']
    removed_user_messages.extend([message['message'] for message in dm_messages if message['u_id'] == user_id])


    # Getting the list of members from the channel and dm
    dm_members = requests.get(config.url + 'dm/details/v1', params={
        'token': auth_user_token,
        'dm_id': dm_id
    }).json()['members']
    dm_members_ids = [user['u_id'] for user in dm_members]

    channel_members = requests.get(config.url + 'channel/details/v2', params={
        'token': auth_user_token,
        'channel_id': channel_id
    }).json()['all_members']
    channel_members_ids = [user['u_id'] for user in channel_members]

    # Getting the list of all users in Streams
    all_users_list = requests.get(config.url + 'users/all/v1', params={'token': auth_user_token}).json()['users']
    all_users_id_list = [user['u_id'] for user in all_users_list]

    # Getting the profile details of the removed user
    removed_user_info = requests.get(config.url + 'user/profile/v1', params={'token': auth_user_token, 'u_id':user_id}).json()['user']
    
    # Setting the email and handle of the auth to the removed user's ones
    setemail_request = requests.put(config.url + 'user/profile/setemail/v1', json={
        'token': auth_user_token,
        'email': removed_user_email
    })
    sethandle_request = requests.put(config.url + 'user/profile/sethandle/v1', json={
        'token': auth_user_token,
        'handle_str': removed_user_handle
    })


    assert r.status_code == 200
    assert all([message == 'Removed user' for message in removed_user_messages])
    assert user_id not in dm_members_ids and user_id not in channel_members_ids
    assert user_id not in all_users_id_list
    assert removed_user_info['name_first'] == 'Removed' and removed_user_info['name_last'] == 'user'
    assert setemail_request.status_code == 200 and sethandle_request.status_code == 200


# Testing the error case of passing in an invalid token
def test_invalid_token(admin_user_remove_url, clear_and_register):
    user_id = clear_and_register['user2_id']

    # Creating an invalid token (empty string)
    invalid_auth_token = ''

    admin_user_remove_input = {
        'token': invalid_auth_token,
        'u_id': user_id
    }
    r = requests.delete(admin_user_remove_url, json=admin_user_remove_input)

    assert r.status_code == AccessError.code

# Testing the error case of passing in an invalid u_id
def test_invalid_u_id(admin_user_remove_url, clear_and_register):
    auth_user_token = clear_and_register['user1_token']
    auth_user_id = clear_and_register['user1_id']
    valid_user_id = clear_and_register['user2_id']

    # Finding an invalid user_id that does not match any existing ids
    invalid_user_id = valid_user_id + 1
    if invalid_user_id == auth_user_id:
        invalid_user_id += 1

    admin_user_remove_input = {
        'token': auth_user_token,
        'u_id': invalid_user_id
    }
    r = requests.delete(admin_user_remove_url, json=admin_user_remove_input)

    assert r.status_code == InputError.code

# Testing the error case of when the auth_user is not a global owner
def test_auth_not_global_owner(admin_user_remove_url, clear_and_register):
    non_global_owner_token = clear_and_register['user2_id']
    non_global_owner_id = clear_and_register['user2_id']

    admin_user_remove_input = {
        'token': non_global_owner_token,
        'u_id': non_global_owner_id
    }
    r = requests.delete(admin_user_remove_url, json=admin_user_remove_input)

    assert r.status_code == AccessError.code

# Testing the error case of when the removed user is the only global owner
def test_user_only_global_owner(admin_user_remove_url, clear_and_register):
    global_owner_token = clear_and_register['user1_token']
    global_owner_id = clear_and_register['user1_id']

    admin_user_remove_input = {
        'token': global_owner_token,
        'u_id': global_owner_id
    }
    r = requests.delete(admin_user_remove_url, json=admin_user_remove_input)

    assert r.status_code == InputError.code

# Testing the error case of when both the auth_user_id and u_id are invalid
def test_invalid_auth_id_and_u_id(admin_user_remove_url, clear_and_register):
    non_global_auth_token = clear_and_register['user2_token']
    non_global_auth_id = clear_and_register['user2_id']
    valid_user_id = clear_and_register['user1_id']

    # Finding an invalid user_id that does not match any existing ids
    invalid_user_id = valid_user_id + 1
    if invalid_user_id == non_global_auth_id:
        invalid_user_id += 1

    admin_user_remove_input = {
        'token': non_global_auth_token,
        'u_id': invalid_user_id
    }
    r = requests.delete(admin_user_remove_url, json=admin_user_remove_input)

    assert r.status_code == AccessError.code

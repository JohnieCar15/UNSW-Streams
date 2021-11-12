import pytest
import requests
from src import config
from src.error import AccessError, InputError

'''
message_remove_v1_test.py: All tests relating to message_remove_v1 function
'''

@pytest.fixture
def register_create():
    '''
    Clears datastore, registers user and creates a channel (making the user a member)
    '''
    requests.delete(config.url + '/clear/v1')

    auth_register_input = {
        'email' : "valid@gmail.com",
        'password' : "password",
        'name_first' : "First",
        'name_last' : "Last",
    }

    user_id = requests.post(config.url + '/auth/register/v2', json=auth_register_input).json()

    channel_create_input = {
        'token' : user_id['token'],
        'name' : "channel",
        'is_public' : True
    }

    channel_id = requests.post(config.url + '/channels/create/v2', json=channel_create_input).json()['channel_id']

    return {
        'valid_token': user_id['token'], 
        'valid_user_id': user_id['auth_user_id'], 
        'valid_channel_id': channel_id
    }

def send_message(register_create, length):
    '''
    HELPER FUNCTION
    Sends a number of messages to specific endpoint
    '''
    send_message_input = {
        'token' : register_create['valid_token'],
        'channel_id': register_create['valid_channel_id'],
        'message': "Hello!"
    }

    message_id_list = []

    for _ in range (length):
        message_id_list.insert(0, requests.post(config.url + '/message/send/v1', json=send_message_input).json()['message_id'])
    
    return {
        'message_id_list' : message_id_list
    }

def get_messages(register_create, start):
    '''
    HELPER FUNCTION
    Creates input for channel_messages and returns messages
    Assumes that tests require valid input, otherwise register_create tokens/channel_ids are directly modified
    '''
    channel_messages_input = {
        'token' : register_create['valid_token'],
        'channel_id' : register_create['valid_channel_id'],
        'start' : start
    }

    channel_messages = requests.get(config.url + '/channel/messages/v2', params=channel_messages_input).json()

    return channel_messages

def test_message_remove(register_create):
    '''
    Test normal functionality of removing one message
    '''
    messagedict = send_message(register_create, 1)

    message_remove_input = {
        'token' : register_create['valid_token'],
        'message_id' : messagedict['message_id_list'][0]
    }

    response = requests.delete(config.url + '/message/remove/v1', json=message_remove_input)
    assert response.status_code == 200

    channel_messages = get_messages(register_create, 0)

    assert channel_messages['messages'] == []

def test_message_remove_multiple(register_create):
    '''
    Tests removing one message with multiple messages saved
    '''
    messagedict = send_message(register_create, 3)

    message_remove_input = {
        'token' : register_create['valid_token'],
        'message_id' : messagedict['message_id_list'][1]
    }

    response = requests.delete(config.url + '/message/remove/v1', json=message_remove_input)
    assert response.status_code == 200

    channel_messages = get_messages(register_create, 0)

    # Check length of message has been reduced by one
    assert(len(channel_messages['messages'])) == 2
    assert channel_messages['messages'][0]['message_id'] == messagedict['message_id_list'][0]
    assert channel_messages['messages'][1]['message_id'] == messagedict['message_id_list'][2]

def test_invalid_message_id(register_create):
    '''
    Tests non-existent message id
    '''
    messagedict = send_message(register_create, 1)

    message_remove_input = {
        'token' : register_create['valid_token'],
        'message_id' : messagedict['message_id_list'][0] + 1
    }

    status = requests.delete(config.url + '/message/remove/v1', json=message_remove_input)

    assert status.status_code == InputError.code

def test_owner_delete(register_create):
    '''
    Tests the owners permission to delete another persons message
    '''
    auth_register_input = {
        'email' : "newperson@gmail.com",
        'password' : "password123",
        'name_first' : "new",
        'name_last' : "person",
    }

    # Register new user
    member = requests.post(config.url + '/auth/register/v2', json=auth_register_input).json()

    join_channel_input = {
        'token' : member['token'],
        'channel_id' : register_create['valid_channel_id']
    }

    # Join channel created initally
    requests.post(config.url + 'channel/join/v2', json=join_channel_input).json()

    send_message_input = {
        'token' : member['token'],
        'channel_id': register_create['valid_channel_id'],
        'message': "Hello!"
    }

    # User sends message to channel
    message_info = requests.post(config.url + '/message/send/v1', json=send_message_input).json()

    message_remove_input = {
        'token' : register_create['valid_token'],
        'message_id' : message_info['message_id']
    }

    # Check owner's ability to delete the member's message
    response = requests.delete(config.url + '/message/remove/v1', json=message_remove_input)
    assert response.status_code == 200

    channel_messages = get_messages(register_create, 0)

    # Also check that the message was successfully removed
    assert channel_messages['messages'] == []

def test_not_owner_remove(register_create):
    '''
    Tests user trying to remove message when not owner or user who created message
    '''
    auth_register_input = {
        'email' : "newperson@gmail.com",
        'password' : "password123",
        'name_first' : "new",
        'name_last' : "person",
    }

    # Register new user
    member = requests.post(config.url + '/auth/register/v2', json=auth_register_input).json()

    join_channel_input = {
        'token' : member['token'],
        'channel_id' : register_create['valid_channel_id']
    }

    # Join channel created initally
    requests.post(config.url + 'channel/join/v2', json=join_channel_input).json()

    send_message_input = {
        'token' : register_create['valid_token'],
        'channel_id': register_create['valid_channel_id'],
        'message': "Hello!"
    }

    # Owner sends message to channel
    message_info = requests.post(config.url + '/message/send/v1', json=send_message_input).json()

    message_delete_input = {
        'token' : member['token'],
        'message_id' : message_info['message_id'],
    }

    # Check user trying to delete message created by owner
    status = requests.delete(config.url + 'message/remove/v1', json=message_delete_input)

    assert status.status_code == AccessError.code 

def test_not_member(register_create):
    '''
    Tests user not member of channel where message is located
    '''
    messagedict = send_message(register_create, 1)

    auth_register_input = {
        'email' : "person@gmail.com",
        'password' : "password123",
        'name_first' : "new",
        'name_last' : "person",
    }

    # Register new user
    user = requests.post(config.url + '/auth/register/v2', json=auth_register_input).json()

    message_delete_input = {
        'token' : user['token'],
        'message_id' : messagedict['message_id_list'][0],
    }

    # User tries to delete message in channel they aren't part of
    status = requests.delete(config.url + 'message/remove/v1', json=message_delete_input)

    assert status.status_code == InputError.code

def test_invalid_token(register_create):
    '''
    Tests invalid token trying to delete message
    '''
    messagedict = send_message(register_create, 1)

    message_remove_input = {
        'token' : " ",
        'message_id' : messagedict['message_id_list'][0]
    }

    status = requests.delete(config.url + '/message/remove/v1', json=message_remove_input)

    assert status.status_code == AccessError.code

def test_invalid_token_invalid_message_id(register_create):
    '''
    Tests invalid token and invalid message id
    '''
    messagedict = send_message(register_create, 1)

    message_remove_input = {
        'token' : " ",
        'message_id' : messagedict['message_id_list'][0] + 1
    }

    status = requests.delete(config.url + '/message/remove/v1', json=message_remove_input)

    assert status.status_code == AccessError.code

def test_dmmessage_remove():
    '''
    Tests normal functionality of removing one message in DM
    '''
    requests.delete(config.url + '/clear/v1')

    auth_register_input = {
        'email' : "valid@gmail.com",
        'password' : "password",
        'name_first' : "First",
        'name_last' : "Last",
    }

    # Register new user
    token = requests.post(config.url + '/auth/register/v2', json=auth_register_input).json()['token']

    dms_create_input = {
        'token': token,
        'u_ids': []
    }

    # Create new DM
    dm_id = requests.post(config.url + 'dm/create/v1', json=dms_create_input).json()['dm_id']

    message_senddm_input = {
        'token': token,
        'dm_id': dm_id,
        'message': "message"
    }

    # User send message to DM
    message_id = requests.post(config.url + 'message/senddm/v1', json=message_senddm_input).json()['message_id']

    message_remove_input = {
        'token' : token,
        'message_id' : message_id,
    }

    # User deletes own message
    requests.delete(config.url + '/message/remove/v1', json=message_remove_input)

    dm_messages_input = {
        'token' : token,
        'dm_id' : dm_id,
        'start' : 0
    }

    dm_messages = requests.get(config.url + 'dm/messages/v1', params=dm_messages_input).json()

    # Check that message was successfully removed
    assert dm_messages['messages'] == []

def test_globalowner_remove_channel():
    '''
    Tests global owner trying to remove message in channel
    '''
    requests.delete(config.url + '/clear/v1')

    auth_register_input1 = {
        'email' : "valid@gmail.com",
        'password' : "password",
        'name_first' : "First",
        'name_last' : "Last",
    }

    # Register first user/global owner
    global_token = requests.post(config.url + '/auth/register/v2', json=auth_register_input1).json()['token'] 

    auth_register_input2 = {
        'email' : "newperson@gmail.com",
        'password' : "password123",
        'name_first' : "New",
        'name_last' : "Person",
    }

    # Register new user
    normal_token = requests.post(config.url + '/auth/register/v2', json=auth_register_input2).json()['token'] 

    channel_create_input = {
        'token' : normal_token,
        'name' : "channel",
        'is_public' : True
    }

    # User creates new channel
    channel_id = requests.post(config.url + '/channels/create/v2', json=channel_create_input).json()['channel_id']

    join_channel_input = {
        'token' : global_token,
        'channel_id' : channel_id
    }

    # Global owner joins channel
    requests.post(config.url + 'channel/join/v2', json=join_channel_input).json()

    send_message_input = {
        'token' : normal_token,
        'channel_id': channel_id,
        'message': "Hello!"
    }   

    # User/owner of channel sends message to channel
    message_id = requests.post(config.url + '/message/send/v1', json=send_message_input).json()['message_id']

    message_remove_input = {
        'token' : global_token,
        'message_id' : message_id,
    }

    # Check that the global owner is able to remove message
    status = requests.delete(config.url + 'message/remove/v1', json=message_remove_input)

    assert status.status_code == 200

    channel_messages_input = {
        'token' : normal_token,
        'channel_id' : channel_id,
        'start' : 0
    }

    channel_messages = requests.get(config.url + '/channel/messages/v2', params=channel_messages_input).json()

    assert channel_messages['messages'] == []

def test_globalowner_remove_dm():
    '''
    Tests global owner trying to remove message in DM
    '''
    requests.delete(config.url + '/clear/v1')

    auth_register_input1 = {
        'email' : "valid@gmail.com",
        'password' : "password",
        'name_first' : "First",
        'name_last' : "Last",
    }

    # Register first user/global owner
    global_member = requests.post(config.url + '/auth/register/v2', json=auth_register_input1).json()

    auth_register_input2 = {
        'email' : "newperson@gmail.com",
        'password' : "password123",
        'name_first' : "First1",
        'name_last' : "Last1",
    }

    # Register new user
    member_token = requests.post(config.url + '/auth/register/v2', json=auth_register_input2).json()['token']

    dms_create_input = {
        'token': member_token,
        'u_ids': [global_member['auth_user_id']]
    }

    # User creates new DM with global owner as member
    dm_id = requests.post(config.url + 'dm/create/v1', json=dms_create_input).json()['dm_id']

    message_senddm_input = {
        'token': member_token,
        'dm_id': dm_id,
        'message': "message"
    }

    # User/owner of DM sends message
    message_id = requests.post(config.url + 'message/senddm/v1', json=message_senddm_input).json()['message_id']

    message_remove_input = {
        'token' : global_member['token'],
        'message_id' : message_id,
    }

    # Check that the global owner is unable to remove message since they have no owner permissions in a DM
    status = requests.delete(config.url + 'message/remove/v1', json=message_remove_input)

    assert status.status_code == AccessError.code


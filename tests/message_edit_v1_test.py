import pytest
import requests
from src import config
from src.error import InputError, AccessError

'''
message_edit_v1_test.py: All tests relating to message_edit_v1 function
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

def test_message_edit(register_create):
    '''
    Tests normal functionality of editing one message
    '''
    messagedict = send_message(register_create, 1)

    message_edit_input = {
        'token' : register_create['valid_token'],
        'message_id' : messagedict['message_id_list'][0],
        'message' : "Universe!"
    }

    requests.put(config.url + '/message/edit/v1', json=message_edit_input)

    channel_messages = get_messages(register_create, 0)

    assert channel_messages['messages'][0]['message'] == "Universe!"

def test_message_edit_multiple_messages(register_create):
    '''
    Tests normal functionality of editing multiple messages
    '''

    messagedict = send_message(register_create, 2)

    message_edit_input1 = {
        'token' : register_create['valid_token'],
        'message_id' : messagedict['message_id_list'][0],
        'message' : "World!"
    }

    # Edit first message
    status1 = requests.put(config.url + '/message/edit/v1', json=message_edit_input1)
    assert status1.status_code == 200

    message_edit_input2 = {
        'token' : register_create['valid_token'],
        'message_id' : messagedict['message_id_list'][1],
        'message' : "Universe!"
    }

    # Edit second message
    status2 = requests.put(config.url + '/message/edit/v1', json=message_edit_input2)
    assert status2.status_code == 200

    channel_messages = get_messages(register_create, 0)

    assert channel_messages['messages'][0]['message'] == 'World!'
    assert channel_messages['messages'][1]['message'] == 'Universe!'


def test_message_delete(register_create):
    '''
    Tests deleting of message using empty string
    '''

    messagedict = send_message(register_create, 1)

    message_edit_input = {
        'token' : register_create['valid_token'],
        'message_id' : messagedict['message_id_list'][0],
        'message' : ""
    }

    status = requests.put(config.url + 'message/edit/v1', json=message_edit_input)
    status.status_code == 200

    channel_messages = get_messages(register_create, 0)

    assert channel_messages['messages'] == []

def test_length_over_1000(register_create):
    '''
    Tests editing message with message over 1000 characters
    '''

    messagedict = send_message(register_create, 1)

    message_edit_input = {
        'token' : register_create['valid_token'],
        'message_id' : messagedict['message_id_list'][0],
        'message' : 'a' * 1001
    }

    status = requests.put(config.url + 'message/edit/v1', json=message_edit_input)

    assert status.status_code == InputError.code

def test_invalid_message_id(register_create):
    '''
    Tests invalid message id
    '''
    messagedict = send_message(register_create, 1)

    message_edit_input = {
        'token' : register_create['valid_token'],
        'message_id' : messagedict['message_id_list'][0] + 1,
        'message' : 'World!'
    }

    status = requests.put(config.url + 'message/edit/v1', json=message_edit_input)

    assert status.status_code == InputError.code

def test_invalid_user(register_create):
    '''
    Tests invalid token attempting to access message
    '''

    messagedict = send_message(register_create, 1)

    message_edit_input = {
        'token' : " ",
        'message_id' : messagedict['message_id_list'][0],
        'message' : 'World!'
    }

    status = requests.put(config.url + 'message/edit/v1', json=message_edit_input)

    assert status.status_code == AccessError.code

def test_not_member(register_create):
    '''
    Tests user not member of channel
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

    message_edit_input = {
        'token' : user['token'],
        'message_id' : messagedict['message_id_list'][0],
        'message' : 'World!'
    }

    status = requests.put(config.url + 'message/edit/v1', json=message_edit_input)

    assert status.status_code == InputError.code

def test_owner_edit(register_create):
    '''
    Tests that the owner of the channel is able to edit message
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

    # Join channel created initially
    requests.post(config.url + 'channel/join/v2', json=join_channel_input).json()

    send_message_input = {
        'token' : member['token'],
        'channel_id': register_create['valid_channel_id'],
        'message': "Hello!"
    }

    # User sends message to channel they just joined
    message_info = requests.post(config.url + '/message/send/v1', json=send_message_input).json()

    message_edit_input = {
        'token' : register_create['valid_token'],
        'message_id' : message_info['message_id'],
        'message' : 'World!'
    }

    # Test that the owner successfully edited the message sent by the new user
    status = requests.put(config.url + 'message/edit/v1', json=message_edit_input)
    status.status_code == 200

    channel_messages = get_messages(register_create, 0)

    assert channel_messages['messages'][0]['message'] == 'World!'

def test_not_owner_edit(register_create):
    '''
    Tests person who did not create message and does not have owner permissions trying to edit message
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

    # Join channel created initially
    requests.post(config.url + 'channel/join/v2', json=join_channel_input).json()

    send_message_input = {
        'token' : register_create['valid_token'],
        'channel_id': register_create['valid_channel_id'],
        'message': "Hello!"
    }

    # Owner sends message to channel
    message_info = requests.post(config.url + '/message/send/v1', json=send_message_input).json()

    message_edit_input = {
        'token' : member['token'],
        'message_id' : message_info['message_id'],
        'message' : 'World!'
    }

    # User attempts to edit the owner's message
    status = requests.put(config.url + 'message/edit/v1', json=message_edit_input)

    assert status.status_code == AccessError.code 


def test_dmmessage_edit():
    '''
    Tests normal funcitonality of editing one message in DM
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

    # User sends message to DM
    message_id = requests.post(config.url + 'message/senddm/v1', json=message_senddm_input).json()['message_id']

    message_edit_input = {
        'token' : token,
        'message_id' : message_id,
        'message' : "Universe!"
    }

    # User edits message
    requests.put(config.url + '/message/edit/v1', json=message_edit_input)

    dm_messages_input = {
        'token' : token,
        'dm_id' : dm_id,
        'start' : 0
    }

    dm_messages = requests.get(config.url + 'dm/messages/v1', params=dm_messages_input).json()

    # Check the message was edited successfully
    assert dm_messages['messages'][0]['message'] == "Universe!"

def test_globalowner_edit_channel():
    '''
    Tests global owner being able to edit inside channel
    '''
    requests.delete(config.url + '/clear/v1')

    auth_register_input1 = {
        'email' : "valid@gmail.com",
        'password' : "password",
        'name_first' : "First",
        'name_last' : "Last",
    }

    # Register first user that is the global owner
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

    # New user creates channel
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

    message_id = requests.post(config.url + '/message/send/v1', json=send_message_input).json()['message_id']

    message_edit_input = {
        'token' : global_token,
        'message_id' : message_id,
        'message' : 'World!'
    }

    status = requests.put(config.url + 'message/edit/v1', json=message_edit_input)
    
    # Check the global owner is able to edit the message
    assert status.status_code == 200

    channel_messages_input = {
        'token' : normal_token,
        'channel_id' : channel_id,
        'start' : 0
    }

    channel_messages = requests.get(config.url + '/channel/messages/v2', params=channel_messages_input).json()

    assert channel_messages['messages'][0]['message'] == 'World!'

def test_globalowner_edit_dm():
    '''
    Tests global owner being unable to edit message in DM
    '''
    requests.delete(config.url + '/clear/v1')

    auth_register_input1 = {
        'email' : "valid@gmail.com",
        'password' : "password",
        'name_first' : "First",
        'name_last' : "Last",
    }

    # Register first user who is global owner
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

    # Create new DM with global owner as member
    dm_id = requests.post(config.url + 'dm/create/v1', json=dms_create_input).json()['dm_id']

    message_senddm_input = {
        'token': member_token,
        'dm_id': dm_id,
        'message': "message"
    }

    # Owner of DM/user sends message
    message_id = requests.post(config.url + 'message/senddm/v1', json=message_senddm_input).json()['message_id']

    message_edit_input = {
        'token' : global_member['token'],
        'message_id' : message_id,
        'message' : "Universe!"
    }

    # Check that the global owner is unable to edit message since they have no owner permissions within DMs
    status = requests.put(config.url + '/message/edit/v1', json=message_edit_input)

    assert status.status_code == AccessError.code




import pytest
import requests
from src import config
from src.error import InputError, AccessError

# Clears datastore, registers user and creates a channel (making the user a member)
@pytest.fixture
def register_create():
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

# HELPER FUNCTION
# Sends a number of messages to specific endpoint
def send_message(register_create, length):
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

# HELPER FUNCTION
# Creates input for channel_messages and returns messages
# Assumes that tests require valid input, otherwise register_create tokens/channel_ids are directly modified
def get_messages(register_create, start):
    channel_messages_input = {
        'token' : register_create['valid_token'],
        'channel_id' : register_create['valid_channel_id'],
        'start' : start
    }

    channel_messages = requests.get(config.url + '/channel/messages/v2', params=channel_messages_input).json()

    return channel_messages

# Tests normal functionality of editing one message
def test_message_edit(register_create):

    messagedict = send_message(register_create, 1)

    message_edit_input = {
        'token' : register_create['valid_token'],
        'message_id' : messagedict['message_id_list'][0],
        'message' : "Universe!"
    }

    requests.put(config.url + '/message/edit/v1', json=message_edit_input)

    channel_messages = get_messages(register_create, 0)

    assert channel_messages['messages'][0]['message'] == "Universe!"

# Tests normal functionality of editing multiple messages
def test_message_edit_multiple_messages(register_create):

    messagedict = send_message(register_create, 2)

    message_edit_input1 = {
        'token' : register_create['valid_token'],
        'message_id' : messagedict['message_id_list'][0],
        'message' : "World!"
    }

    status1 = requests.put(config.url + '/message/edit/v1', json=message_edit_input1)
    assert status1.status_code == 200

    message_edit_input2 = {
        'token' : register_create['valid_token'],
        'message_id' : messagedict['message_id_list'][1],
        'message' : "Universe!"
    }

    status2 = requests.put(config.url + '/message/edit/v1', json=message_edit_input2)
    assert status2.status_code == 200

    channel_messages = get_messages(register_create, 0)

    assert channel_messages['messages'][0]['message'] == 'World!'
    assert channel_messages['messages'][1]['message'] == 'Universe!'

# Tests deleting of message using empty string
def test_message_delete(register_create):
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

# Tests editing message with message over 1000 characters
def test_length_over_1000(register_create):
    messagedict = send_message(register_create, 1)

    message_edit_input = {
        'token' : register_create['valid_token'],
        'message_id' : messagedict['message_id_list'][0],
        'message' : 'a' * 1001
    }

    status = requests.put(config.url + 'message/edit/v1', json=message_edit_input)

    assert status.status_code == InputError.code


# Tests invalid message id
def test_invalid_message_id(register_create):
    messagedict = send_message(register_create, 1)

    message_edit_input = {
        'token' : register_create['valid_token'],
        'message_id' : messagedict['message_id_list'][0] + 1,
        'message' : 'World!'
    }

    status = requests.put(config.url + 'message/edit/v1', json=message_edit_input)

    assert status.status_code == InputError.code

# Tests invalid token attempting to access message
def test_invalid_user(register_create):
    messagedict = send_message(register_create, 1)

    message_edit_input = {
        'token' : " ",
        'message_id' : messagedict['message_id_list'][0],
        'message' : 'World!'
    }

    status = requests.put(config.url + 'message/edit/v1', json=message_edit_input)

    assert status.status_code == AccessError.code

def test_not_member(register_create):
    messagedict = send_message(register_create, 1)

    auth_register_input = {
        'email' : "person@gmail.com",
        'password' : "password123",
        'name_first' : "new",
        'name_last' : "person",
    }

    user = requests.post(config.url + '/auth/register/v2', json=auth_register_input).json()

    message_edit_input = {
        'token' : user['token'],
        'message_id' : messagedict['message_id_list'][0],
        'message' : 'World!'
    }

    status = requests.put(config.url + 'message/edit/v1', json=message_edit_input)

    assert status.status_code == InputError.code

# Tests that the owner of the channel is able to edit message
def test_owner_edit(register_create):

    auth_register_input = {
        'email' : "newperson@gmail.com",
        'password' : "password123",
        'name_first' : "new",
        'name_last' : "person",
    }

    member = requests.post(config.url + '/auth/register/v2', json=auth_register_input).json()

    join_channel_input = {
        'token' : member['token'],
        'channel_id' : register_create['valid_channel_id']
    }

    requests.post(config.url + 'channel/join/v2', json=join_channel_input).json()

    send_message_input = {
        'token' : member['token'],
        'channel_id': register_create['valid_channel_id'],
        'message': "Hello!"
    }

    message_info = requests.post(config.url + '/message/send/v1', json=send_message_input).json()

    message_edit_input = {
        'token' : register_create['valid_token'],
        'message_id' : message_info['message_id'],
        'message' : 'World!'
    }

    status = requests.put(config.url + 'message/edit/v1', json=message_edit_input)
    status.status_code == 200

    channel_messages = get_messages(register_create, 0)

    assert channel_messages['messages'][0]['message'] == 'World!'

def test_not_owner_edit(register_create):
 
    auth_register_input = {
        'email' : "newperson@gmail.com",
        'password' : "password123",
        'name_first' : "new",
        'name_last' : "person",
    }

    member = requests.post(config.url + '/auth/register/v2', json=auth_register_input).json()

    join_channel_input = {
        'token' : member['token'],
        'channel_id' : register_create['valid_channel_id']
    }

    requests.post(config.url + 'channel/join/v2', json=join_channel_input).json()

    send_message_input = {
        'token' : register_create['valid_token'],
        'channel_id': register_create['valid_channel_id'],
        'message': "Hello!"
    }

    message_info = requests.post(config.url + '/message/send/v1', json=send_message_input).json()

    message_edit_input = {
        'token' : member['token'],
        'message_id' : message_info['message_id'],
        'message' : 'World!'
    }

    status = requests.put(config.url + 'message/edit/v1', json=message_edit_input)

    assert status.status_code == AccessError.code 


# Tests normal functionality of editing one message
def test_dmmessage_edit():
    requests.delete(config.url + '/clear/v1')

    auth_register_input = {
        'email' : "valid@gmail.com",
        'password' : "password",
        'name_first' : "First",
        'name_last' : "Last",
    }

    token = requests.post(config.url + '/auth/register/v2', json=auth_register_input).json()['token']

    dms_create_input = {
        'token': token,
        'u_ids': []
    }

    dm_id = requests.post(config.url + 'dm/create/v1', json=dms_create_input).json()['dm_id']

    message_senddm_input = {
        'token': token,
        'dm_id': dm_id,
        'message': "message"
    }

    message_id = requests.post(config.url + 'message/senddm/v1', json=message_senddm_input).json()['message_id']

    message_edit_input = {
        'token' : token,
        'message_id' : message_id,
        'message' : "Universe!"
    }

    requests.put(config.url + '/message/edit/v1', json=message_edit_input)

    dm_messages_input = {
        'token' : token,
        'dm_id' : dm_id,
        'start' : 0
    }

    dm_messages = requests.get(config.url + 'dm/messages/v1', params=dm_messages_input).json()

    assert dm_messages['messages'][0]['message'] == "Universe!"

def test_globalowner_edit_channel():
    requests.delete(config.url + '/clear/v1')

    auth_register_input1 = {
        'email' : "valid@gmail.com",
        'password' : "password",
        'name_first' : "First",
        'name_last' : "Last",
    }

    global_token = requests.post(config.url + '/auth/register/v2', json=auth_register_input1).json()['token'] 

    auth_register_input2 = {
        'email' : "newperson@gmail.com",
        'password' : "password123",
        'name_first' : "New",
        'name_last' : "Person",
    }

    normal_token = requests.post(config.url + '/auth/register/v2', json=auth_register_input2).json()['token'] 

    channel_create_input = {
        'token' : normal_token,
        'name' : "channel",
        'is_public' : True
    }

    channel_id = requests.post(config.url + '/channels/create/v2', json=channel_create_input).json()['channel_id']

    join_channel_input = {
        'token' : global_token,
        'channel_id' : channel_id
    }

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
    
    assert status.status_code == 200

    channel_messages_input = {
        'token' : normal_token,
        'channel_id' : channel_id,
        'start' : 0
    }

    channel_messages = requests.get(config.url + '/channel/messages/v2', params=channel_messages_input).json()

    assert channel_messages['messages'][0]['message'] == 'World!'

def test_globalowner_edit_dm():
    requests.delete(config.url + '/clear/v1')

    auth_register_input1 = {
        'email' : "valid@gmail.com",
        'password' : "password",
        'name_first' : "First",
        'name_last' : "Last",
    }

    global_member = requests.post(config.url + '/auth/register/v2', json=auth_register_input1).json()

    auth_register_input2 = {
        'email' : "newperson@gmail.com",
        'password' : "password123",
        'name_first' : "First1",
        'name_last' : "Last1",
    }

    member_token = requests.post(config.url + '/auth/register/v2', json=auth_register_input2).json()['token']

    dms_create_input = {
        'token': member_token,
        'u_ids': [global_member['auth_user_id']]
    }

    dm_id = requests.post(config.url + 'dm/create/v1', json=dms_create_input).json()['dm_id']

    message_senddm_input = {
        'token': member_token,
        'dm_id': dm_id,
        'message': "message"
    }

    message_id = requests.post(config.url + 'message/senddm/v1', json=message_senddm_input).json()['message_id']

    message_edit_input = {
        'token' : global_member['token'],
        'message_id' : message_id,
        'message' : "Universe!"
    }

    status = requests.put(config.url + '/message/edit/v1', json=message_edit_input)

    assert status.status_code == AccessError.code




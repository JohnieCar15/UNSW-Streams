import pytest
import requests
from src import config
from src.error import AccessError, InputError

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
# Returns a list of message ids, from oldest to newest
def send_message(register_create, length):
    send_message_input = {
        'token' : register_create['valid_token'],
        'channel_id': register_create['valid_channel_id'],
        'message': "Hello!"
    }

    message_id_list = []

    for x in range (length):
        message_id_list.insert(0, requests.post(config.url + '/message/send/v1', json=send_message_input)['message_id'])
    
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

# Test normal functionality of removing one message
def test_message_remove(register_create):
    messagedict = send_message(register_create, 1)

    message_remove_input = {
        'token' : register_create['valid_token'],
        'message_id' : messagedict['message_id_list'][0]
    }

    requests.delete(config.url + '/message/remove/v1', params=message_remove_input)

    channel_messages = get_messages(register_create, 0)

    assert channel_messages['messages'] == []

# Tests removing one message with multiple messages saved
def test_message_remove_multiple(register_create):
    messagedict = send_message(register_create, 3)

    message_remove_input = {
        'token' : register_create['valid_token'],
        'message_id' : messagedict['message_id_list'][1]
    }

    requests.delete(config.url + '/message/remove/v1', params=message_remove_input)

    channel_messages = get_messages(register_create, 0)

    assert channel_messages['messages'] == [
        {
            'message_id' : messagedict['message_id_list'][0],
            'u_id' : register_create['valid_user_id'],
            'message' : "Hello!"
        },
        {
            'message_id' : messagedict['message_id_list'][2],
            'u_id' : register_create['valid_user_id'],
            'message' : "Hello!"
        }
    ]

# Tests non-existent message id
def test_invalid_message_id(register_create):
    messagedict = send_message(register_create, 1)

    message_remove_input = {
        'token' : register_create['valid_token'],
        'message_id' : messagedict['message_id_list'][0] + 1
    }

    status = requests.delete(config.url + '/message/remove/v1', params=message_remove_input)

    assert status.status_code == InputError.code

# Tests the owners permission to delete another persons message
def test_owner_delete(register_create):
    auth_register_input = {
        'email' : "valid@gmail.com",
        'password' : "password",
        'name_first' : "First",
        'name_last' : "Last",
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

    message_info = requests.post(config.url + '/message/send/v1', json=send_message_input)

    message_remove_input = {
        'token' : register_create['valid_token'],
        'message_id' : message_info['message_id']
    }

    requests.delete(config.url + '/message/remove/v1', params=message_remove_input)

    channel_messages = get_messages(register_create, 0)

    assert channel_messages['messages'] == []

# Tests invalid token trying to delete message
def test_invalid_token(register_create):
    messagedict = send_message(register_create, 1)

    message_remove_input = {
        'token' : register_create['valid_token'] + 1,
        'message_id' : messagedict['message_id_list'][0]
    }

    status = requests.delete(config.url + '/message/remove/v1', params=message_remove_input)

    assert status.status_code == AccessError.code

# Tests invalid token and invalid message id
def test_invalid_token_invalid_message_id(register_create):
    messagedict = send_message(register_create, 1)

    message_remove_input = {
        'token' : register_create['valid_token'] + 1,
        'message_id' : messagedict['message_id_list'][0] + 1
    }

    status = requests.delete(config.url + '/message/remove/v1', params=message_remove_input)

    assert status.status_code == AccessError.code




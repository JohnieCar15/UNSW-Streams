import pytest
import requests
from src import config
from src.error import InputError, AccessError
from datetime import datetime

# Clears datastore, registers user and creates a channel (making the user a member)
@pytest.fixture
def register_create_channel():
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

# HELPER FUNCTION
# Pins message given a message id
def pin_message(token, message_id):
    message_pin_input = {
        'token' : token,
        'message_id' : message_id 
    }

    requests.post(config.url + 'message/pin/v1', json=message_pin_input).json()

def test_unpinned_normal(register_create_channel):

    messagedict = send_message(register_create_channel, 1)

    pin_message(register_create_channel['valid_token'], messagedict['message_id_list'][0])

    channel_messages1 = get_messages(register_create_channel, 0)

    assert channel_messages1['messages'][0]['is_pinned'] == True

    message_unpin_input = {
        'token' : register_create_channel['valid_token'],
        'message_id' : messagedict['message_id_list'][0]      
    }

    requests.post(config.url + 'message/unpin/v1', json=message_unpin_input).json()

    channel_messages2 = get_messages(register_create_channel, 0)

    assert channel_messages2['messages'][0]['is_pinned'] == False


def test_invalid_message_id(register_create_channel):

    messagedict = send_message(register_create_channel, 1)

    pin_message(register_create_channel['valid_token'], messagedict['message_id_list'][0])

    message_unpin_input = {
        'token' : register_create_channel['valid_token'],
        'message_id' : messagedict['message_id_list'][0] + 1
    }

    status = requests.post(config.url + 'message/unpin/v1', json=message_unpin_input)

    assert status.status_code == InputError.code

def test_already_unpinned(register_create_channel):

    messagedict = send_message(register_create_channel, 1)

    message_unpin_input = {
        'token' : register_create_channel['valid_token'],
        'message_id' : messagedict['message_id_list'][0]
    }

    status = requests.post(config.url + 'message/unpin/v1', json=message_unpin_input)

    assert status.status_code == InputError.code

def test_invalid_token(register_create_channel):

    messagedict = send_message(register_create_channel, 1)

    message_unpin_input = {
        'token' : " ",
        'message_id' : messagedict['message_id_list'][0]
    }

    status = requests.post(config.url + 'message/unpin/v1', json=message_unpin_input)

    assert status.status_code == AccessError.code

def test_not_owner(register_create_channel):
    auth_register_input = {
        'email' : "newperson@gmail.com",
        'password' : "password",
        'name_first' : "First",
        'name_last' : "Last",
    }

    member = requests.post(config.url + '/auth/register/v2', json=auth_register_input).json()

    channel_join_input = {
        'token': member['token'],
        'channel_id': register_create_channel['valid_channel_id']
    }

    requests.post(config.url + 'channel/join/v2', json=channel_join_input).json()

    messagedict = send_message(register_create_channel, 1)

    pin_message(register_create_channel['valid_token'], messagedict['message_id_list'][0])

    message_unpin_input = {
        'token' : member['token'],
        'message_id' : messagedict['message_id_list'][0]
    }

    status = requests.post(config.url + 'message/unpin/v1', json=message_unpin_input)

    assert status.status_code == AccessError.code
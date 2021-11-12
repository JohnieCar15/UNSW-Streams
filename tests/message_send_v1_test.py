import pytest
import requests
from src import config
from src.error import AccessError, InputError

'''
message_send_v1_test.py: All tests relating to message_send_v1 function
'''

@pytest.fixture
def message_send_url():
    return config.url + 'message/send/v1'

@pytest.fixture
def clear_and_register():
    '''
    Clears datastore, registers user and creates channel, making the user the owner
    '''
    requests.delete(config.url + 'clear/v1')

    auth_register_input = {
        'email':'user@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last': 'Last'
    }
    token = requests.post(config.url + 'auth/register/v2', json=auth_register_input).json()['token']

    channels_create_input = {
        'token': token,
        'name': "channel",
        'is_public': True
    }
    channel_id = requests.post(config.url + 'channels/create/v2', json=channels_create_input).json()['channel_id']

    return {'token': token, 'channel_id': channel_id}

def test_single_message(message_send_url, clear_and_register):
    '''
    Testing the general case of sending a single message
    '''
    token = clear_and_register['token']
    channel_id = clear_and_register['channel_id']

    message_send_input = {
        'token': token,
        'channel_id': channel_id,
        'message': "message"
    }
    requests.post(message_send_url, json=message_send_input)

    channel_messages_input = {
        'token': token,
        'channel_id': channel_id,
        'start': 0
    }
    channel_messages = requests.get(config.url + 'channel/messages/v2', params=channel_messages_input).json()['messages']
    channel_messages = [message['message'] for message in channel_messages]
    assert channel_messages == ["message"]

def test_multiple_messages(message_send_url, clear_and_register):
    '''
    Testing the case of sending multiple messages
    '''
    token = clear_and_register['token']
    channel_id = clear_and_register['channel_id']

    message_send_input1 = {
        'token': token,
        'channel_id': channel_id,
        'message': "message1"
    }
    # Send first message
    requests.post(message_send_url, json=message_send_input1)

    message_send_input2 = {
        'token': token,
        'channel_id': channel_id,
        'message': "message2"
    }

    # Send second message
    requests.post(message_send_url, json=message_send_input2)

    channel_messages_input = {
        'token': token,
        'channel_id': channel_id,
        'start': 0
    }
    channel_messages = requests.get(config.url + 'channel/messages/v2', params=channel_messages_input).json()['messages']
    channel_messages = [message['message'] for message in channel_messages]
    assert channel_messages == ["message2", "message1"]

def test_invalid_token(message_send_url, clear_and_register):
    '''
    Testing the error case of passing in an invalid token
    '''
    channel_id = clear_and_register['channel_id']

    # Generating an invalid token that does not match existing tokens
    message_send_input = {
        'token': None,
        'channel_id': channel_id,
        'message': "message"
    }
    r = requests.post(message_send_url, json=message_send_input)

    # Throws AccessError
    assert r.status_code == AccessError.code

def test_invalid_channel_id(message_send_url, clear_and_register):
    '''
    Testing the error case of passing in an invalid channel_id
    '''
    token = clear_and_register['token']
    valid_channel_id = clear_and_register['channel_id']

    # Generating an invalid channel_id that does not match existing channel_ids
    invalid_channel_id = valid_channel_id + 1

    message_send_input = {
        'token': token,
        'channel_id': invalid_channel_id,
        'message': "message"
    }
    r = requests.post(message_send_url, json=message_send_input)

    # Throws InputError
    assert r.status_code == InputError.code

def test_message_too_short(message_send_url, clear_and_register):
    '''
    Testing the error case of sending a message that is too short
    '''
    token = clear_and_register['token']
    channel_id = clear_and_register['channel_id']

    message_send_input = {
        'token': token,
        'channel_id': channel_id,
        'message': ""
    }
    r = requests.post(message_send_url, json=message_send_input)

    # Throws InputError
    assert r.status_code == InputError.code

def test_message_too_long(message_send_url, clear_and_register):
    '''
    Testing the error case of sending a message that is too long
    '''
    token = clear_and_register['token']
    channel_id = clear_and_register['channel_id']

    message_send_input = {
        'token': token,
        'channel_id': channel_id,
        'message': "a" * 1001
    }
    r = requests.post(message_send_url, json=message_send_input)

    # Throws InputError
    assert r.status_code == InputError.code

def test_all_invalid_inputs(message_send_url, clear_and_register):
    '''
    Testing the error case of passing in an invalid token, channel_id and message
    '''
    valid_channel_id = clear_and_register['channel_id']

    # Generating an invalid channel_id that does not match existing channel_ids
    invalid_channel_id = valid_channel_id + 1

    message_send_input = {
        'token': None,
        'channel_id': invalid_channel_id,
        'message': "message"
    }
    r = requests.post(message_send_url, json=message_send_input)

    # Throws AccessError
    assert r.status_code == AccessError.code

def test_not_member_of_channel(message_send_url, clear_and_register):
    '''
    Testing the error case of sending a message when not a member of the channel
    '''
    channel_id = clear_and_register['channel_id']
    auth_register_input = {
        'email':'new@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last': 'Last'
    }
    non_member_id = requests.post(config.url + 'auth/register/v2', json=auth_register_input).json()['token']

    message_send_input = {
        'token': non_member_id,
        'channel_id': channel_id,
        'message': "message"
    }
    r = requests.post(message_send_url, json=message_send_input)

    # Throws AccessError
    assert r.status_code == AccessError.code


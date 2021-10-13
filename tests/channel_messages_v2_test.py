import pytest
import requests
from datetime import datetime
from src import config

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

    timelist = []
    message_id_list = []

    for x in range (length):
        message_id_list.append(requests.post(config.url + '/message/send/v1', json=send_message_input)['message_id'])
        timelist.append(datetime.now())
    
    return {
        'timelist' : timelist,
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

# Tests case where there are no messages
def test_empty(register_create):

    channel_messages = get_messages(register_create, 0)
    
    assert(channel_messages['messages']) == []
    assert(channel_messages['start']) == 0
    assert(channel_messages['end']) == -1

# Tests case for one message, starting at 0th index, less than 50 messages
def test_one_message(register_create):

    messagedict = send_message(register_create, 1) 

    channel_messages = get_messages(register_create, 0)

    assert(channel_messages['messages']) == [
        {
            'message_id' : messagedict['message_id_list'][0],
            'u_id' : register_create['valid_user_id'],
            'message' : "Hello!",
            'time_created' : messagedict['timelist'][0]
        }
    ]
    assert(channel_messages['start']) == 0
    assert(channel_messages['end']) == -1

# Tests case for two messages, starting at the 0th index, less than 50 messages
def test_two_messages(register_create):
    messagedict = send_message(register_create, 2)

    channel_messages = get_messages(register_create, 0)

    assert(channel_messages['messages']) == [
        {
            'message_id' : messagedict['message_id_list'][0],
            'u_id' : register_create['valid_user_id'],
            'message' : "Hello!",
            'time_created' : messagedict['timelist'][0]
        },
        {
            'message_id' : messagedict['message_id_list'][1],
            'u_id' : register_create['valid_user_id'],
            'message' : "World!",
            'time_created' : messagedict['timelist'][1]
        }

    ]
    assert(channel_messages['start']) == 0
    assert(channel_messages['end']) == -1

# Tests case for more than 50 messages, starting at 0th index
def test_more_than_50_messages_first_index(register_create):
    messagedict = send_message(register_create, 100)

    channel_messages = get_messages(register_create, 0)

    for i in range(0, 50):
        assert(channel_messages['messages'][i]) == {
            'message_id' : messagedict['message_id_list'][i],
            'u_id' : register_create['valid_user_id'],
            'message' : "Hello!",
            'time_created' : messagedict['timelist'][i]
        }
    assert(channel_messages['start']) == 0
    assert(channel_messages['end']) == 50

# Tests case for more than 50 messages, starting at different index
def test_more_than_50_messages_different_index(register_create):
    messagedict = send_message(register_create, 100)

    channel_messages = get_messages(register_create, 6)

    for i in range(0, 50):
        assert(channel_messages['messages'][i]) == {
            'message_id' : messagedict['message_id_list'][i + 6],
            'u_id' : register_create['valid_user_id'],
            'message' : "Hello!",
            'time_created' : messagedict['timelist'][i + 6]
        }
    assert(channel_messages['start']) == 6
    assert(channel_messages['end']) == 56

# Tests case for less than 50 messages, starting at first index
def test_less_than_50_messages_first_index(register_create):
    messagedict = send_message(register_create, 30)

    channel_messages = get_messages(register_create, 0)

    for i in range(0, 30):
        assert(channel_messages['messages'][i]) == {
            'message_id' : messagedict['message_id_list'][i],
            'u_id' : register_create['valid_user_id'],
            'message' : "Hello!",
            'time_created' : messagedict['timelist'][i]
        }
    assert(channel_messages['start']) == 0
    assert(channel_messages['end']) == -1

# Tests case for less than 50 messages, starting at different index
def test_less_than_50_messages_different_index(register_create):
    messagedict = send_message(register_create, 30)

    channel_messages = get_messages(register_create, 7)

    for i in range(0, 23):
        assert(channel_messages['messages'][i]) == {
            'message_id' : messagedict['message_id_list'][i + 7],
            'u_id' : register_create['valid_user_id'],
            'message' : "Hello!",
            'time_created' : messagedict['timelist'][i + 7]
        }
    assert(channel_messages['start']) == 7
    assert(channel_messages['end']) == -1

# Tests invalid start with no messages in datastore
def test_invalid_start_no_messages(register_create):

    channel_messages = get_messages(register_create, 20)

    assert channel_messages.status_code == 400

# Tests invalid start with one message
def test_invalid_start_one_message(register_create):
    messagedict = send_message(register_create, 1)
    
    channel_messages = get_messages(register_create, 2)

    assert channel_messages.status_code == 400

# Tests invalid channel id and valid user id
def test_invalid_channel_id(register_create):

    channel_messages_input = {
        'token' : register_create['valid_token'],
        'channel_id' : register_create['valid_channel_id'] + 1,
        'start' : 0
    }

    channel_messages = requests.get(config.url + '/channel/messages/v2', params=channel_messages_input).json()
    assert channel_messages.status_code == 400

# Tests valid channel id and invalid user id
def test_invalid_user_id(register_create):
    channel_messages_input = {
        'token' : register_create['valid_token'] + 1,
        'channel_id' : register_create['valid_channel_id'],
        'start' : 0
    }

    channel_messages = requests.get(config.url + '/channel/messages/v2', params=channel_messages_input).json()
    assert channel_messages.status_code == 403


# Tests invalid start and invalid user id
def test_invalid_start_invalid_id(register_create):
    channel_messages_input = {
        'token' : register_create['valid_token'] + 1,
        'channel_id' : register_create['valid_channel_id'],
        'start' : 3
    }

    channel_messages = requests.get(config.url + '/channel/messages/v2', params=channel_messages_input).json()
    assert channel_messages.status_code == 403

# Tests invalid start and invalid channel id
def test_invalid_start_invalid_channel(register_create):
    channel_messages_input = {
        'token' : register_create['valid_token'],
        'channel_id' : register_create['valid_channel_id'] + 1,
        'start' : 3
    }

    channel_messages = requests.get(config.url + '/channel/messages/v2', params=channel_messages_input).json()
    assert channel_messages.status_code == 403








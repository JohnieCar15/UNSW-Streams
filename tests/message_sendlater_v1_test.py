import pytest
import requests
import time
from src import config
from src.error import InputError, AccessError
from datetime import datetime

'''
message_sendlater_v1_test.py: All tests relating to message_sendlater_v1 function
'''

@pytest.fixture
def register_create():
    '''
    Clears datastore, registers user and creates channel, making the user the owner
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

def test_normal(register_create):
    '''
    Tests normal functionality of sending messages later
    '''
    message_sendlater_input = {
        'token' : register_create['valid_token'],
        'channel_id' : register_create['valid_channel_id'],
        'message' : "Hello!",
        'time_sent' : int(datetime.utcnow().timestamp()) + 3
    }

    message_id = requests.post(config.url + '/message/sendlater/v1', json=message_sendlater_input).json()['message_id']

    # Check initally before the message is due to be set that the message store is empty
    channel_messages1 = get_messages(register_create, 0)

    assert channel_messages1['messages'] == []

    # Wait 3 seconds
    time.sleep(3)

    # Check after 3 seconds that the message has appeared in the datastore
    channel_messages = get_messages(register_create, 0)

    assert channel_messages['messages'][0]['message_id'] == message_id
    assert channel_messages['messages'][0]['u_id'] == register_create['valid_user_id']
    assert channel_messages['messages'][0]['message'] == "Hello!"
    assert abs(int(datetime.utcnow().timestamp()) - channel_messages['messages'][0]['time_created']) < 2

def test_send_message_inbetween(register_create):
    '''
    Tests sending a message after message send later is called, ensures that original message id is maintained
    '''
    message_sendlater_input = {
        'token' : register_create['valid_token'],
        'channel_id' : register_create['valid_channel_id'],
        'message' : "World!",
        'time_sent' : int(datetime.utcnow().timestamp()) + 3
    }

    message_id = requests.post(config.url + '/message/sendlater/v1', json=message_sendlater_input).json()['message_id']

    message_send_input = {
        'token' : register_create['valid_token'],
        'channel_id' : register_create['valid_channel_id'],
        'message' : "Hello!",
    }

    # Send a message before the sendlater message is due to be sent
    requests.post(config.url + '/message/send/v1', json=message_send_input).json()['message_id']

    # Wait 3 seconds
    time.sleep(3)

    channel_messages = get_messages(register_create, 0)

    # Assert that the sendlater message is the most recent message in the channel
    assert channel_messages['messages'][0]['message_id'] == message_id
    assert channel_messages['messages'][0]['u_id'] == register_create['valid_user_id']
    assert channel_messages['messages'][0]['message'] == "World!"
    assert abs(int(datetime.utcnow().timestamp()) - channel_messages['messages'][0]['time_created']) < 2

def test_invalid_token(register_create):
    '''
    Test invalid token
    '''
    message_sendlater_input = {
        'token' : " ",
        'channel_id' : register_create['valid_channel_id'],
        'message' : "Hello!",
        'time_sent' : int(datetime.utcnow().timestamp()) + 3
    }

    status = requests.post(config.url + '/message/sendlater/v1', json=message_sendlater_input)

    assert status.status_code == AccessError.code

def test_invalid_channel_id(register_create):
    '''
    Tests invalid channel id
    '''
    message_sendlater_input = {
        'token' : register_create['valid_token'],
        'channel_id' : register_create['valid_channel_id'] + 1,
        'message' : "Hello!",
        'time_sent' : int(datetime.utcnow().timestamp()) + 5
    }

    status = requests.post(config.url + '/message/sendlater/v1', json=message_sendlater_input)

    assert status.status_code == InputError.code

def test_invalid_message_over_1000(register_create):
    '''
    Tests message over 1000 characters
    '''
    message_sendlater_input = {
        'token' : register_create['valid_token'],
        'channel_id' : register_create['valid_channel_id'],
        'message' : 'a' * 1001,
        'time_sent' : int(datetime.utcnow().timestamp()) + 5
    }

    status = requests.post(config.url + '/message/sendlater/v1', json=message_sendlater_input)

    assert status.status_code == InputError.code

def test_invalid_message_empty(register_create):
    '''
    Tests empty message
    '''
    message_sendlater_input = {
        'token' : register_create['valid_token'],
        'channel_id' : register_create['valid_channel_id'],
        'message' : "",
        'time_sent' : int(datetime.utcnow().timestamp()) + 5
    }

    status = requests.post(config.url + '/message/sendlater/v1', json=message_sendlater_input)

    assert status.status_code == InputError.code

def test_invalid_time(register_create):
    '''
    Tests invalid time (time sent in past)
    '''
    message_sendlater_input = {
        'token' : register_create['valid_token'],
        'channel_id' : register_create['valid_channel_id'],
        'message' : "Hello!",
        'time_sent' : int(datetime.utcnow().timestamp()) - 5
    }

    status = requests.post(config.url + '/message/sendlater/v1', json=message_sendlater_input)

    assert status.status_code == InputError.code

def test_not_part_of_channel(register_create):
    '''
    Tests user not part of channel
    '''
    auth_register_input = {
        'email' : "newpersond@gmail.com",
        'password' : "password123",
        'name_first' : "New",
        'name_last' : "Person",
    }

    # Register new user
    user_token = requests.post(config.url + '/auth/register/v2', json=auth_register_input).json()['token']

    message_sendlater_input = {
        'token' : user_token,
        'channel_id' : register_create['valid_channel_id'],
        'message' : "Hello!",
        'time_sent' : int(datetime.utcnow().timestamp()) + 5
    }

    status = requests.post(config.url + '/message/sendlater/v1', json=message_sendlater_input)

    assert status.status_code == AccessError.code

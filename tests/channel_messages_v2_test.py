import pytest
import requests
from datetime import datetime, timezone
from src import channel, config
from src.error import AccessError, InputError

'''
channel_messages_v2_test.py: All tests relating to channel_messages_v2 function
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

    # Register user. This user is the global owner
    user_id = requests.post(config.url + '/auth/register/v2', json=auth_register_input).json()

    channel_create_input = {
        'token' : user_id['token'],
        'name' : "channel",
        'is_public' : True
    }

    # Creating new channel
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
    timelist = []
    message_id_list = []

    # Send a number of new messages to a specific channel
    for x in range (length):
        send_message_input = {
            'token' : register_create['valid_token'],
            'channel_id': register_create['valid_channel_id'],
            'message': f"Hello!{x}"
        }
        # Append time created of message to timelist
        timelist.insert(0, int(datetime.now(timezone.utc).timestamp()))
        # Append message IDs to message_id_list
        message_id_list.insert(0, requests.post(config.url + '/message/send/v1', json=send_message_input).json()['message_id'])
    
    return {
        'timelist' : timelist,
        'message_id_list' : message_id_list
    }

def get_messages(register_create, start):
    '''
    HELPER FUNCTION
    Creates input for channel_messages and returns messages. Assumes that tests require valid input, otherwise register_create tokens/channel_ids are directly modified
    '''
    channel_messages_input = {
        'token' : register_create['valid_token'],
        'channel_id' : register_create['valid_channel_id'],
        'start' : start
    }

    channel_messages = requests.get(config.url + '/channel/messages/v2', params=channel_messages_input).json()

    return channel_messages

def test_empty(register_create):
    '''
    Tests case where there are no messages
    '''
    channel_messages = get_messages(register_create, 0)
    
    assert channel_messages['messages'] == []
    assert channel_messages['start'] == 0
    assert channel_messages['end'] == -1


def test_one_message(register_create):
    '''
    Tests one message present in datastore, starting at 0th index
    '''
    messagedict = send_message(register_create, 1)

    channel_messages = get_messages(register_create, 0)

    assert channel_messages['messages'][0]['message_id'] == messagedict['message_id_list'][0]
    assert channel_messages['messages'][0]['u_id'] == register_create['valid_user_id']
    assert channel_messages['messages'][0]['message'] == "Hello!0"
    assert abs((channel_messages['messages'][0]['time_created'] - messagedict['timelist'][0])) < 2

    assert channel_messages['start'] == 0
    assert channel_messages['end'] == -1


def test_two_messages(register_create):
    '''
    Tests for two messages present in the datastore, starting at 0th index
    '''
    messagedict = send_message(register_create, 2)

    channel_messages = get_messages(register_create, 0)
    
    for x in range (2):
        assert channel_messages['messages'][x]['message_id'] == messagedict['message_id_list'][x]
        assert channel_messages['messages'][x]['u_id'] == register_create['valid_user_id']
        assert channel_messages['messages'][x]['message'] == f"Hello!{1 - x}"
        assert abs((channel_messages['messages'][x]['time_created'] - messagedict['timelist'][x])) < 2

    assert channel_messages['start'] == 0
    assert channel_messages['end'] == -1

def test_more_than_50_messages_first_index(register_create):
    '''
    Tests for more than 50 messages in store, starting at the 0th index
    '''
    messagedict = send_message(register_create, 55)

    channel_messages = get_messages(register_create, 0)

    for x in range(0, 50):
        assert channel_messages['messages'][x]['message_id'] == messagedict['message_id_list'][x]
        assert channel_messages['messages'][x]['u_id'] == register_create['valid_user_id']
        assert channel_messages['messages'][x]['message'] == f"Hello!{54 - x}"
        assert abs((channel_messages['messages'][x]['time_created'] - messagedict['timelist'][x])) < 2

    assert channel_messages['start'] == 0
    assert channel_messages['end'] == 50

def test_more_than_50_messages_different_index(register_create):
    '''
    Tests more than 50 messages starting at a different index
    '''
    messagedict = send_message(register_create, 60)

    channel_messages = get_messages(register_create, 6)

    for x in range(0, 50):
        assert channel_messages['messages'][x]['message_id'] == messagedict['message_id_list'][x + 6]
        assert channel_messages['messages'][x]['u_id'] == register_create['valid_user_id']
        assert channel_messages['messages'][x]['message'] == f"Hello!{(59 - 6) - x}"
        assert abs((channel_messages['messages'][x]['time_created'] - messagedict['timelist'][x])) < 2

    assert channel_messages['start'] == 6
    assert channel_messages['end'] == 56

def test_less_than_50_messages_first_index(register_create):
    '''
    Tests case for less than 50 messages, starting at first index
    '''
    messagedict = send_message(register_create, 30)

    channel_messages = get_messages(register_create, 0)

    for x in range(0, 30):
        assert channel_messages['messages'][x]['message_id'] == messagedict['message_id_list'][x]
        assert channel_messages['messages'][x]['u_id'] == register_create['valid_user_id']
        assert channel_messages['messages'][x]['message'] == f"Hello!{29 - x}"
        assert abs((channel_messages['messages'][x]['time_created'] - messagedict['timelist'][x])) < 2

    assert channel_messages['start'] == 0
    assert channel_messages['end'] == -1

def test_less_than_50_messages_different_index(register_create):
    '''
    Tests case for less than 50 messages, starting at different index
    '''
    messagedict = send_message(register_create, 30)

    channel_messages = get_messages(register_create, 7)

    for x in range(0, 23):
        assert channel_messages['messages'][x]['message_id'] == messagedict['message_id_list'][x + 7]
        assert channel_messages['messages'][x]['u_id'] == register_create['valid_user_id']
        assert channel_messages['messages'][x]['message'] == f"Hello!{(29 - 7) - x}"
        assert abs((channel_messages['messages'][x]['time_created'] - messagedict['timelist'][x])) < 2

    assert channel_messages['start'] == 7
    assert channel_messages['end'] == -1

def test_invalid_start_no_messages(register_create):
    '''
    Tests invalid start with no messages in datastore
    '''
    channel_messages_input = {
        'token' : register_create['valid_token'],
        'channel_id' : register_create['valid_channel_id'],
        'start' : 20
    }

    channel_messages = requests.get(config.url + '/channel/messages/v2', params=channel_messages_input).json()

    assert channel_messages['code'] == InputError.code

def test_invalid_start_one_message(register_create):
    '''
    Tests invalid start with one message
    '''
    send_message(register_create, 1)
    
    channel_messages = get_messages(register_create, 2)

    assert channel_messages['code'] == InputError.code

def test_invalid_channel_id(register_create):
    '''
    Tests invalid channel id and valid token
    '''
    channel_messages_input = {
        'token' : register_create['valid_token'],
        'channel_id' : register_create['valid_channel_id'] + 10,
        'start' : 0
    }

    channel_messages = requests.get(config.url + '/channel/messages/v2', params=channel_messages_input).json()
    assert channel_messages['code'] == InputError.code

def test_invalid_token(register_create):
    '''
    Tests valid channel id and invalid token
    '''
    channel_messages_input = {
        'token' : " ",
        'channel_id' : register_create['valid_channel_id'],
        'start' : 0
    }

    channel_messages = requests.get(config.url + '/channel/messages/v2', params=channel_messages_input).json()
    assert channel_messages['code'] == AccessError.code

def test_invalid_start_invalid_token(register_create):
    '''
    Tests invalid start and invalid token
    '''
    channel_messages_input = {
        'token' : " ",
        'channel_id' : register_create['valid_channel_id'],
        'start' : 3
    }

    channel_messages = requests.get(config.url + '/channel/messages/v2', params=channel_messages_input).json()
    assert channel_messages['code'] == AccessError.code

def test_invalid_start_invalid_channel(register_create):
    '''
    Tests invalid start and invalid channel id
    '''
    channel_messages_input = {
        'token' : register_create['valid_token'],
        'channel_id' : register_create['valid_channel_id'] + 1,
        'start' : 3
    }

    channel_messages = requests.get(config.url + '/channel/messages/v2', params=channel_messages_input).json()
    assert channel_messages['code'] == InputError.code

def test_negative_start(register_create):
    '''
    Test invalid start (negative)
    '''
    channel_messages_input = {
        'token' : register_create['valid_token'],
        'channel_id' : register_create['valid_channel_id'],
        'start' : -5
    }

    channel_messages = requests.get(config.url + '/channel/messages/v2', params=channel_messages_input).json()
    assert channel_messages['code'] == InputError.code

def test_not_part_of_channel(register_create):
    '''
    Test user not part of channel
    '''
    auth_register_input = {
        'email' : "validperson@gmail.com",
        'password' : "password123",
        'name_first' : "new",
        'name_last' : "person",
    }

    # Register new user
    new_person = requests.post(config.url + '/auth/register/v2', json=auth_register_input).json()

    channel_messages_input = {
        'token' : new_person['token'],
        'channel_id' : register_create['valid_channel_id'],
        'start' : 0
    }

    channel_messages = requests.get(config.url + '/channel/messages/v2', params=channel_messages_input).json()
    assert channel_messages['code'] == AccessError.code








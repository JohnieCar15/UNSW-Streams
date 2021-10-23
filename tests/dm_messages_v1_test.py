import pytest
import requests
from datetime import datetime
from src import config
from src.error import AccessError, InputError

# Note that the 0th index is the newest message

# Clears datastore, registers two users and creates a dm towards another user
@pytest.fixture
def register_create():
    requests.delete(config.url + 'clear/v1')

    auth_register_input1 = {
        'email' : "valid@gmail.com",
        'password' : "password",
        'name_first' : "First",
        'name_last' : "Last",
    }

    user_id1 = requests.post(config.url + 'auth/register/v2', json=auth_register_input1).json()

    auth_register_input2 = {
        'email' : "newperson@gmail.com",
        'password' : "password123",
        'name_first' : "new",
        'name_last' : "person",
    }

    user_id2 = requests.post(config.url + 'auth/register/v2', json=auth_register_input2).json()

    dm_create_input = {
        'token' : user_id1['token'],
        'u_ids' : [user_id2['auth_user_id']]
    }

    dm_id = requests.post(config.url + 'dm/create/v1', json=dm_create_input).json()['dm_id']

    return {
        'valid_token_owner': user_id1['token'], 
        'valid_token_member' : user_id2['token'],
        'valid_user_id': user_id1['auth_user_id'], 
        'valid_dm_id': dm_id
    }

# HELPER FUNCTION
# Sends a number of messages to specific endpoint
def send_message(register_create, length):
    send_messagedm_input = {
        'token' : register_create['valid_token_owner'],
        'dm_id': register_create['valid_dm_id'],
        'message': "Hello!"
    }

    timelist = []
    message_id_list = []

    for _ in range (length):
        timelist.insert(0, int(datetime.utcnow().timestamp()))
        message_id_list.insert(0, requests.post(config.url + 'message/senddm/v1', json=send_messagedm_input).json()['message_id'])
    
    return {
        'timelist' : timelist,
        'message_id_list' : message_id_list
    }

# HELPER FUNCTION
# Creates input for dm_messages and returns messages
# Assumes that tests require valid input, otherwise register_create tokens/dm_ids are directly modified
def get_messages(register_create, start):
    dm_messages_input = {
        'token' : register_create['valid_token_owner'],
        'dm_id' : register_create['valid_dm_id'],
        'start' : start
    }

    dm_messages = requests.get(config.url + 'dm/messages/v1', params=dm_messages_input)


    return dm_messages

# HELPER FUNCTION
# Checks if time provided in dm_messages is within two seconds of sending message request
# Returns original time of dm_messages if true (to allow assertion), else returns False
def time_in_range(new_time, dm_messages, length):
    difference = new_time - dm_messages['messages']['time_created'][length]

    if difference.TotalSeconds < 2:
        return dm_messages['messages']['time_created'][length]
    else:
        return False

# Tests case where there are no messages
def test_empty(register_create):

    dm_messages = get_messages(register_create, 0).json()
    
    assert dm_messages['messages'] == []
    assert dm_messages['start'] == 0
    assert dm_messages['end'] == -1


# Tests case for one message, starting at 0th index, less than 50 messages
def test_one_message(register_create):

    messagedict = send_message(register_create, 1) 

    dm_messages = get_messages(register_create, 0).json()

    assert dm_messages['messages'][0]['message_id'] == messagedict['message_id_list'][0]
    assert dm_messages['messages'][0]['u_id'] == register_create['valid_user_id']
    assert dm_messages['messages'][0]['message'] == "Hello!"
    assert abs((dm_messages['messages'][0]['time_created'] - messagedict['timelist'][0])) < 2
    assert dm_messages['start'] == 0
    assert dm_messages['end'] == -1

# Tests case for two messages, starting at the 0th index, less than 50 messages
def test_two_messages(register_create):
    messagedict = send_message(register_create, 2)

    dm_messages = get_messages(register_create, 0).json()

    for x in range (2):
        assert dm_messages['messages'][x]['message_id'] == messagedict['message_id_list'][x]
        assert dm_messages['messages'][x]['u_id'] == register_create['valid_user_id']
        assert dm_messages['messages'][x]['message'] == "Hello!"
        assert abs((dm_messages['messages'][x]['time_created'] - messagedict['timelist'][x])) < 2

    assert dm_messages['start'] == 0
    assert dm_messages['end'] == -1

# Tests case for more than 50 messages, starting at 0th index
def test_more_than_50_messages_first_index(register_create):
    messagedict = send_message(register_create, 100)

    dm_messages = get_messages(register_create, 0).json()

    for x in range(0, 50):
        assert dm_messages['messages'][x]['message_id'] == messagedict['message_id_list'][x]
        assert dm_messages['messages'][x]['u_id'] == register_create['valid_user_id']
        assert dm_messages['messages'][x]['message'] == "Hello!"
        assert abs((dm_messages['messages'][x]['time_created'] - messagedict['timelist'][x])) < 2

    assert dm_messages['start'] == 0
    assert dm_messages['end'] == 50

# Tests case for more than 50 messages, starting at different index
def test_more_than_50_messages_different_index(register_create):
    messagedict = send_message(register_create, 100)

    dm_messages = get_messages(register_create, 6).json()

    for x in range(0, 50):
        assert dm_messages['messages'][x]['message_id'] == messagedict['message_id_list'][x + 6]
        assert dm_messages['messages'][x]['u_id'] == register_create['valid_user_id']
        assert dm_messages['messages'][x]['message'] == "Hello!"
        assert abs((dm_messages['messages'][x]['time_created'] - messagedict['timelist'][x])) < 2


    assert dm_messages['start'] == 6
    assert dm_messages['end'] == 56

# Tests case for less than 50 messages, starting at first index
def test_less_than_50_messages_first_index(register_create):
    messagedict = send_message(register_create, 30)

    dm_messages = get_messages(register_create, 0).json()

    for x in range(0, 30):
        assert dm_messages['messages'][x]['message_id'] == messagedict['message_id_list'][x]
        assert dm_messages['messages'][x]['u_id'] == register_create['valid_user_id']
        assert dm_messages['messages'][x]['message'] == "Hello!"
        assert abs((dm_messages['messages'][x]['time_created'] - messagedict['timelist'][x])) < 2
        
    assert dm_messages['start'] == 0
    assert dm_messages['end'] == -1

# Tests case for less than 50 messages, starting at different index
def test_less_than_50_messages_different_index(register_create):
    messagedict = send_message(register_create, 30)

    dm_messages = get_messages(register_create, 7).json()

    for x in range(0, 23):
        assert dm_messages['messages'][x]['message_id'] == messagedict['message_id_list'][x + 7]
        assert dm_messages['messages'][x]['u_id'] == register_create['valid_user_id']
        assert dm_messages['messages'][x]['message'] == "Hello!"
        assert abs((dm_messages['messages'][x]['time_created'] - messagedict['timelist'][x])) < 2

    assert dm_messages['start'] == 7
    assert dm_messages['end'] == -1

# Tests invalid start with no messages in datastore
def test_invalid_start_no_messages(register_create):

    dm_messages = get_messages(register_create, 20)

    assert dm_messages.status_code == InputError.code

# Tests invalid start with one message
def test_invalid_start_one_message(register_create):
    send_message(register_create, 1)
    
    dm_messages = get_messages(register_create, 2)

    assert dm_messages.status_code == InputError.code

# Tests invalid dm id and valid user id
def test_invalid_dm_id(register_create):

    dm_messages_input = {
        'token' : register_create['valid_token_owner'],
        'dm_id' : register_create['valid_dm_id'] + 1,
        'start' : 0
    }

    dm_messages = requests.get(config.url + 'dm/messages/v1', params=dm_messages_input)
    assert dm_messages.status_code == InputError.code

# Tests valid dm id and invalid token
def test_invalid_token_owner(register_create):
    dm_messages_input = {
        'token' : register_create['valid_token_owner'] + register_create['valid_token_member'],
        'dm_id' : register_create['valid_dm_id'],
        'start' : 0
    }

    dm_messages = requests.get(config.url + 'dm/messages/v1', params=dm_messages_input)
    assert dm_messages.status_code == AccessError.code


# Tests invalid start and invalid token
def test_invalid_start_invalid_token_owner(register_create):
    dm_messages_input = {
        'token' : register_create['valid_token_owner'] + register_create['valid_token_member'],
        'dm_id' : register_create['valid_dm_id'],
        'start' : 3
    }

    dm_messages = requests.get(config.url + 'dm/messages/v1', params=dm_messages_input)
    assert dm_messages.status_code == AccessError.code

# Tests invalid start and invalid dm id
def test_invalid_start_invalid_dm(register_create):
    dm_messages_input = {
        'token' : register_create['valid_token_owner'],
        'dm_id' : register_create['valid_dm_id'] + 1,
        'start' : 3
    }

    dm_messages = requests.get(config.url + 'dm/messages/v1', params=dm_messages_input)
    assert dm_messages.status_code == InputError.code

# Test invalid start (negative)
def test_negative_start(register_create):
    dm_messages_input = {
        'token' : register_create['valid_token_owner'],
        'dm_id' : register_create['valid_dm_id'],
        'start' : -5
    }

    dm_messages = requests.get(config.url + '/dm/messages/v1', params=dm_messages_input).json()
    assert dm_messages['code'] == InputError.code

def test_not_part_of_dm(register_create):
    auth_register_input = {
        'email' : "validperson@gmail.com",
        'password' : "password123",
        'name_first' : "new",
        'name_last' : "person",
    }

    new_person = requests.post(config.url + '/auth/register/v2', json=auth_register_input).json()

    dm_messages_input = {
        'token' : new_person['token'],
        'dm_id' : register_create['valid_dm_id'],
        'start' : 0
    }

    dm_messages = requests.get(config.url + '/dm/messages/v1', params=dm_messages_input).json()
    assert dm_messages['code'] == AccessError.code
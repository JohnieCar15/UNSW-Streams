import pytest
import requests
from datetime import datetime, timezone
from src import config
from src.error import AccessError, InputError

'''
dm_messages_v1_test.py: All tests relating to dm_messages_v1 function
'''

@pytest.fixture
def register_create():
    '''
    Clears datastore, registers two users and creates a dm towards another user
    '''
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

def send_message(register_create, length):
    '''
    HELPER FUNCTION
    Sends a number of messages to specific endpoint
    '''
    send_messagedm_input = {
        'token' : register_create['valid_token_owner'],
        'dm_id': register_create['valid_dm_id'],
        'message': "Hello!"
    }

    timelist = []
    message_id_list = []

    for _ in range (length):
        timelist.insert(0, int(datetime.now(timezone.utc).timestamp()))
        message_id_list.insert(0, requests.post(config.url + 'message/senddm/v1', json=send_messagedm_input).json()['message_id'])
    
    return {
        'timelist' : timelist,
        'message_id_list' : message_id_list
    }

def get_messages(register_create, start):
    '''
    HELPER FUNCTION
    Creates input for dm_messages and returns messages
    Assumes that tests require valid input, otherwise register_create tokens/dm_ids are directly modified
    '''
    dm_messages_input = {
        'token' : register_create['valid_token_owner'],
        'dm_id' : register_create['valid_dm_id'],
        'start' : start
    }

    dm_messages = requests.get(config.url + 'dm/messages/v1', params=dm_messages_input)


    return dm_messages

def test_empty(register_create):
    '''
    Tests case where there are no messages
    '''
    dm_messages = get_messages(register_create, 0).json()
    
    assert dm_messages['messages'] == []
    assert dm_messages['start'] == 0
    assert dm_messages['end'] == -1

def test_one_message(register_create):
    '''
    Tests one message present in datastore, starting at 0th index
    '''
    messagedict = send_message(register_create, 1) 

    dm_messages = get_messages(register_create, 0).json()

    assert dm_messages['messages'][0]['message_id'] == messagedict['message_id_list'][0]
    assert dm_messages['messages'][0]['u_id'] == register_create['valid_user_id']
    assert dm_messages['messages'][0]['message'] == "Hello!"
    assert abs((dm_messages['messages'][0]['time_created'] - messagedict['timelist'][0])) < 2
    assert dm_messages['start'] == 0
    assert dm_messages['end'] == -1

def test_two_messages(register_create):
    '''
    Tests for two messages present in the datastore, starting at 0th index
    '''
    messagedict = send_message(register_create, 2)

    dm_messages = get_messages(register_create, 0).json()

    for x in range (2):
        assert dm_messages['messages'][x]['message_id'] == messagedict['message_id_list'][x]
        assert dm_messages['messages'][x]['u_id'] == register_create['valid_user_id']
        assert dm_messages['messages'][x]['message'] == "Hello!"
        assert abs((dm_messages['messages'][x]['time_created'] - messagedict['timelist'][x])) < 2

    assert dm_messages['start'] == 0
    assert dm_messages['end'] == -1

def test_more_than_50_messages_first_index(register_create):
    '''
    Tests for more than 50 messages in store, starting at the 0th index
    '''
    messagedict = send_message(register_create, 100)

    dm_messages = get_messages(register_create, 0).json()

    for x in range(0, 50):
        assert dm_messages['messages'][x]['message_id'] == messagedict['message_id_list'][x]
        assert dm_messages['messages'][x]['u_id'] == register_create['valid_user_id']
        assert dm_messages['messages'][x]['message'] == "Hello!"
        assert abs((dm_messages['messages'][x]['time_created'] - messagedict['timelist'][x])) < 2

    assert dm_messages['start'] == 0
    assert dm_messages['end'] == 50

def test_more_than_50_messages_different_index(register_create):
    '''
    Tests more than 50 messages starting at a different index
    '''
    messagedict = send_message(register_create, 100)

    dm_messages = get_messages(register_create, 6).json()

    for x in range(0, 50):
        assert dm_messages['messages'][x]['message_id'] == messagedict['message_id_list'][x + 6]
        assert dm_messages['messages'][x]['u_id'] == register_create['valid_user_id']
        assert dm_messages['messages'][x]['message'] == "Hello!"
        assert abs((dm_messages['messages'][x]['time_created'] - messagedict['timelist'][x])) < 2


    assert dm_messages['start'] == 6
    assert dm_messages['end'] == 56

def test_less_than_50_messages_first_index(register_create):
    '''
    Tests case for less than 50 messages, starting at first index
    '''
    messagedict = send_message(register_create, 30)

    dm_messages = get_messages(register_create, 0).json()

    for x in range(0, 30):
        assert dm_messages['messages'][x]['message_id'] == messagedict['message_id_list'][x]
        assert dm_messages['messages'][x]['u_id'] == register_create['valid_user_id']
        assert dm_messages['messages'][x]['message'] == "Hello!"
        assert abs((dm_messages['messages'][x]['time_created'] - messagedict['timelist'][x])) < 2
        
    assert dm_messages['start'] == 0
    assert dm_messages['end'] == -1

def test_less_than_50_messages_different_index(register_create):
    '''
    Tests case for less than 50 messages, starting at different index
    '''
    messagedict = send_message(register_create, 30)

    dm_messages = get_messages(register_create, 7).json()

    for x in range(0, 23):
        assert dm_messages['messages'][x]['message_id'] == messagedict['message_id_list'][x + 7]
        assert dm_messages['messages'][x]['u_id'] == register_create['valid_user_id']
        assert dm_messages['messages'][x]['message'] == "Hello!"
        assert abs((dm_messages['messages'][x]['time_created'] - messagedict['timelist'][x])) < 2

    assert dm_messages['start'] == 7
    assert dm_messages['end'] == -1

def test_invalid_start_no_messages(register_create):
    '''
    Tests invalid start with no messages in datastore
    '''
    dm_messages = get_messages(register_create, 20)

    assert dm_messages.status_code == InputError.code

def test_invalid_start_one_message(register_create):
    '''
    Tests invalid start with one message
    '''
    send_message(register_create, 1)
    
    dm_messages = get_messages(register_create, 2)

    assert dm_messages.status_code == InputError.code

def test_invalid_dm_id(register_create):
    '''
    Tests invalid dm id and valid token
    '''
    dm_messages_input = {
        'token' : register_create['valid_token_owner'],
        'dm_id' : register_create['valid_dm_id'] + 1,
        'start' : 0
    }

    dm_messages = requests.get(config.url + 'dm/messages/v1', params=dm_messages_input)
    assert dm_messages.status_code == InputError.code

def test_invalid_token_owner(register_create):
    '''
    Tests valid dm id and invalid token
    '''
    dm_messages_input = {
        'token' : register_create['valid_token_owner'] + register_create['valid_token_member'],
        'dm_id' : register_create['valid_dm_id'],
        'start' : 0
    }

    dm_messages = requests.get(config.url + 'dm/messages/v1', params=dm_messages_input)
    assert dm_messages.status_code == AccessError.code


def test_invalid_start_invalid_token_owner(register_create):
    '''
    Tests invalid start and invalid token
    '''
    dm_messages_input = {
        'token' : register_create['valid_token_owner'] + register_create['valid_token_member'],
        'dm_id' : register_create['valid_dm_id'],
        'start' : 3
    }

    dm_messages = requests.get(config.url + 'dm/messages/v1', params=dm_messages_input)
    assert dm_messages.status_code == AccessError.code

def test_invalid_start_invalid_dm(register_create):
    '''
    Tests invalid start and invalid dm id
    '''
    dm_messages_input = {
        'token' : register_create['valid_token_owner'],
        'dm_id' : register_create['valid_dm_id'] + 1,
        'start' : 3
    }

    dm_messages = requests.get(config.url + 'dm/messages/v1', params=dm_messages_input)
    assert dm_messages.status_code == InputError.code

def test_negative_start(register_create):
    '''
    Test invalid start (negative)
    '''
    dm_messages_input = {
        'token' : register_create['valid_token_owner'],
        'dm_id' : register_create['valid_dm_id'],
        'start' : -5
    }

    dm_messages = requests.get(config.url + '/dm/messages/v1', params=dm_messages_input).json()
    assert dm_messages['code'] == InputError.code

def test_not_part_of_dm(register_create):
    '''
    Test user not part of dm
    '''
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
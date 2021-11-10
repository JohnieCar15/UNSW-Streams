import pytest
import requests
import time
from src import config
from src.error import InputError, AccessError
from datetime import datetime

# Clears datastore, registers user and creates a dm (making the user a member)
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

    dm_create_input = {
        'token' : user_id['token'],
        'u_ids' : []
    }

    dm_id = requests.post(config.url + '/dm/create/v1', json=dm_create_input).json()['dm_id']

    return {
        'valid_token': user_id['token'], 
        'valid_user_id': user_id['auth_user_id'], 
        'valid_dm_id': dm_id
    }


# HELPER FUNCTION
# Creates input for dm_messages and returns messages
# Assumes that tests require valid input, otherwise register_create tokens/dm_ids are directly modified
def get_messages(register_create, start):
    dm_messages_input = {
        'token' : register_create['valid_token'],
        'dm_id' : register_create['valid_dm_id'],
        'start' : start
    }

    dm_messages = requests.get(config.url + '/dm/messages/v1', params=dm_messages_input).json()

    return dm_messages

def test_normal(register_create):
    '''
    Tests normal functionality of sending messages later
    '''
    message_sendlaterdm_input = {
        'token' : register_create['valid_token'],
        'dm_id' : register_create['valid_dm_id'],
        'message' : "Hello!",
        'time_sent' : int(datetime.utcnow().timestamp()) + 3
    }

    message_id = requests.post(config.url + '/message/sendlaterdm/v1', json=message_sendlaterdm_input).json()['message_id']

    dm_messages1 = get_messages(register_create, 0)

    assert dm_messages1['messages'] == []

    time.sleep(3)

    dm_messages = get_messages(register_create, 0)

    assert dm_messages['messages'][0]['message_id'] == message_id
    assert dm_messages['messages'][0]['u_id'] == register_create['valid_user_id']
    assert dm_messages['messages'][0]['message'] == "Hello!"
    assert abs(int(datetime.utcnow().timestamp()) - dm_messages['messages'][0]['time_created']) < 2

def test_send_message_inbetween(register_create):
    '''
    Tests sending a message after message send later is called, ensures that original message id is maintained
    '''
    message_sendlaterdm_input = {
        'token' : register_create['valid_token'],
        'dm_id' : register_create['valid_dm_id'],
        'message' : "World!",
        'time_sent' : int(datetime.utcnow().timestamp()) + 3
    }

    message_id = requests.post(config.url + '/message/sendlaterdm/v1', json=message_sendlaterdm_input).json()['message_id']

    message_senddm_input = {
        'token' : register_create['valid_token'],
        'dm_id' : register_create['valid_dm_id'],
        'message' : "Hello!",
    }

    requests.post(config.url + '/message/senddm/v1', json=message_senddm_input).json()['message_id']

    time.sleep(3)

    dm_messages = get_messages(register_create, 0)

    assert dm_messages['messages'][0]['message_id'] == message_id
    assert dm_messages['messages'][0]['u_id'] == register_create['valid_user_id']
    assert dm_messages['messages'][0]['message'] == "World!"
    assert abs(int(datetime.utcnow().timestamp()) - dm_messages['messages'][0]['time_created']) < 2

def test_invalid_token(register_create):
    '''
    Test invalid token
    '''
    message_sendlaterdm_input = {
        'token' : " ",
        'dm_id' : register_create['valid_dm_id'],
        'message' : "Hello!",
        'time_sent' : int(datetime.utcnow().timestamp()) + 3
    }

    status = requests.post(config.url + '/message/sendlaterdm/v1', json=message_sendlaterdm_input)

    assert status.status_code == AccessError.code

def test_invalid_dm_id(register_create):
    '''
    Tests invalid dm id
    '''
    message_sendlaterdm_input = {
        'token' : register_create['valid_token'],
        'dm_id' : register_create['valid_dm_id'] + 1,
        'message' : "Hello!",
        'time_sent' : int(datetime.utcnow().timestamp()) + 5
    }

    status = requests.post(config.url + '/message/sendlaterdm/v1', json=message_sendlaterdm_input)

    assert status.status_code == InputError.code

def test_invalid_message_over_1000(register_create):
    '''
    Tests message over 1000 characters
    '''
    message_sendlaterdm_input = {
        'token' : register_create['valid_token'],
        'dm_id' : register_create['valid_dm_id'],
        'message' : 'a' * 1001,
        'time_sent' : int(datetime.utcnow().timestamp()) + 5
    }

    status = requests.post(config.url + '/message/sendlaterdm/v1', json=message_sendlaterdm_input)

    assert status.status_code == InputError.code

def test_invalid_message_empty(register_create):
    '''
    Tests empty message
    '''
    message_sendlaterdm_input = {
        'token' : register_create['valid_token'],
        'dm_id' : register_create['valid_dm_id'],
        'message' : "",
        'time_sent' : int(datetime.utcnow().timestamp()) + 5
    }

    status = requests.post(config.url + '/message/sendlaterdm/v1', json=message_sendlaterdm_input)

    assert status.status_code == InputError.code

def test_invalid_time(register_create):
    '''
    Tests invalid time (time sent in past)
    '''
    message_sendlaterdm_input = {
        'token' : register_create['valid_token'],
        'dm_id' : register_create['valid_dm_id'],
        'message' : "Hello!",
        'time_sent' : int(datetime.utcnow().timestamp()) - 5
    }

    status = requests.post(config.url + '/message/sendlaterdm/v1', json=message_sendlaterdm_input)

    assert status.status_code == InputError.code

def test_not_part_of_dm(register_create):
    '''
    Tests user not part of DM
    '''
    auth_register_input = {
        'email' : "newpersond@gmail.com",
        'password' : "password123",
        'name_first' : "New",
        'name_last' : "Person",
    }

    user_token = requests.post(config.url + '/auth/register/v2', json=auth_register_input).json()['token']


    message_sendlaterdm_input = {
        'token' : user_token,
        'dm_id' : register_create['valid_dm_id'],
        'message' : "Hello!",
        'time_sent' : int(datetime.utcnow().timestamp()) + 5
    }

    status = requests.post(config.url + '/message/sendlaterdm/v1', json=message_sendlaterdm_input)

    assert status.status_code == AccessError.code
    requests.delete(config.url + '/clear/v1')

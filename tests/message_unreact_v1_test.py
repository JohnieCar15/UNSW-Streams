import pytest
import requests
from src import config
from src.error import InputError, AccessError

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

# Clears datastore, registers user and creates a dm (making the user a member)
@pytest.fixture
def register_create_dm():
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
# Creates a react for a function given a token and message_id
def react_message(token, message_id):
    message_react_input = {
        'token' : token,
        'message_id' : message_id,
        'react_id' : 1
    }

    requests.post(config.url + '/message/react/v1', json=message_react_input).json()  



def test_normal_unreact_channel(register_create_channel):
    '''
    Test normal unreact of user in channel
    '''
    messagedict = send_message(register_create_channel, 1)

    react_message(register_create_channel['valid_token'], messagedict['message_id_list'][0])

    message_unreact_input = {
        'token' : register_create_channel['valid_token'],
        'message_id' : messagedict['message_id_list'][0],
        'react_id' : 1
    }

    requests.post(config.url + '/message/unreact/v1', json=message_unreact_input).json()


    channel_messages = get_messages(register_create_channel, 0)

    assert channel_messages['messages'][0]['reacts'][0] == {
        'react_id' : 1,
        'u_ids' : [],
        'is_this_user_reacted' : False
    }

def test_normal_unreact_dm(register_create_dm):
    '''
    Tests normal unreact of user in dm
    '''
    send_messagedm_input = {
        'token' : register_create_dm['valid_token'],
        'dm_id': register_create_dm['valid_dm_id'],
        'message': "Hello!"
    }

    message_id = requests.post(config.url + '/message/senddm/v1', json=send_messagedm_input).json()['message_id']

    react_message(register_create_dm['valid_token'], message_id)

    message_unreact_input = {
        'token' : register_create_dm['valid_token'],
        'message_id' : message_id,
        'react_id' : 1
    }

    requests.post(config.url + '/message/unreact/v1', json=message_unreact_input).json()

    dm_messages_input = {
        'token' : register_create_dm['valid_token'],
        'dm_id' : register_create_dm['valid_dm_id'],
        'start' : 0
    }

    dm_messages = requests.get(config.url + '/dm/messages/v1', params=dm_messages_input).json()

    assert dm_messages['messages'][0]['reacts'][0] == {
        'react_id' : 1,
        'u_ids' : [],
        'is_this_user_reacted' : False
    }


def test_member_unreact(register_create_channel):
    '''
    Tests a member unreacting to a message
    '''
   
    messagedict = send_message(register_create_channel, 1)

    auth_register_input = {
        'email' : "newperson@gmail.com",
        'password' : "password123",
        'name_first' : "New",
        'name_last' : "Person",
    }

    member = requests.post(config.url + '/auth/register/v2', json=auth_register_input).json()
    
    channel_join_input = {
        'token' : member['token'],
        'channel_id' : register_create_channel['valid_channel_id']
    }

    requests.post(config.url + '/channel/join/v2', json=channel_join_input)

    react_message(register_create_channel['valid_token'], messagedict['message_id_list'][0])
    react_message(member['token'], messagedict['message_id_list'][0])

    message_unreact_input = {
        'token' : member['token'],
        'message_id' : messagedict['message_id_list'][0],
        'react_id' : 1
    }

    requests.post(config.url + '/message/unreact/v1', json=message_unreact_input).json()


    channel_messages = get_messages(register_create_channel, 0)

    assert channel_messages['messages'][0]['reacts'][0] == {
        'react_id' : 1,
        'u_ids' : [register_create_channel['valid_user_id']],
        'is_this_user_reacted' : True
    } 


def test_invalid_message_id(register_create_channel):
    '''
    Test invalid message id
    '''

    messagedict = send_message(register_create_channel, 1)
    
    react_message(register_create_channel['valid_token'], messagedict['message_id_list'][0])

    message_unreact_input = {
        'token' : register_create_channel['valid_token'],
        'message_id' : messagedict['message_id_list'][0] + 1,
        'react_id' : 1
    }

    status = requests.post(config.url + '/message/unreact/v1', json=message_unreact_input)

    assert status.status_code == InputError.code

def test_invalid_react_id(register_create_channel):
    '''
    Test invalid react id
    '''

    messagedict = send_message(register_create_channel, 1)

    react_message(register_create_channel['valid_token'], messagedict['message_id_list'][0])

    message_unreact_input = {
        'token' : register_create_channel['valid_token'],
        'message_id' : messagedict['message_id_list'][0],
        'react_id' : 5
    }

    status = requests.post(config.url + '/message/unreact/v1', json=message_unreact_input)

    assert status.status_code == InputError.code

def test_no_react(register_create_channel):
    '''
    Test unreacting a message that hasn't been reacted
    '''
    messagedict = send_message(register_create_channel, 1)

    message_unreact_input = {
        'token' : register_create_channel['valid_token'],
        'message_id' : messagedict['message_id_list'][0],
        'react_id' : 1
    }

    status = requests.post(config.url + '/message/unreact/v1', json=message_unreact_input)

    assert status.status_code == InputError.code

def test_invalid_token(register_create_channel):
    '''
    Tests invalid token
    '''

    messagedict = send_message(register_create_channel, 1)

    react_message(register_create_channel['valid_token'], messagedict['message_id_list'][0])

    message_unreact_input = {
        'token' : " ",
        'message_id' : messagedict['message_id_list'][0],
        'react_id' : 1
    }

    status = requests.post(config.url + '/message/unreact/v1', json=message_unreact_input)

    assert status.status_code == AccessError.code

def test_not_part_of_channel(register_create_channel):
    '''
    Tests user unreacting message they have reacted to and aren't part of channel
    '''
    messagedict = send_message(register_create_channel, 1)

    auth_register_input = {
        'email' : "newperson@gmail.com",
        'password' : "password123",
        'name_first' : "New",
        'name_last' : "Person",
    }

    member = requests.post(config.url + '/auth/register/v2', json=auth_register_input).json()

    channel_join_input = {
        'token' : member['token'],
        'channel_id' : register_create_channel['valid_channel_id']
    }

    requests.post(config.url + '/channel/join/v2', json=channel_join_input)

    message_react_input = {
        'token' : member['token'],
        'message_id' : messagedict['message_id_list'][0],
        'react_id' : 1
    }

    requests.post(config.url + '/message/react/v1', json=message_react_input).json()

    channel_leave_input = {
        'token' : member['token'],
        'channel_id' : register_create_channel['valid_channel_id']
    }

    requests.post(config.url + '/channel/leave/v1', json=channel_leave_input).json()

    message_unreact_input = {
        'token' : member['token'],
        'message_id' : messagedict['message_id_list'][0],
        'react_id' : 1
    }

    status = requests.post(config.url + '/message/unreact/v1', json=message_unreact_input)

    assert status.status_code == AccessError.code

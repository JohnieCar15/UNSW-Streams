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

# Clears datastore, registers user and creates a dm (making the user a member)
@pytest.fixture
def register_create_dm():
    requests.delete(config.url + 'clear/v1')

    auth_register_input = {
        'email' : "valid@gmail.com",
        'password' : "password",
        'name_first' : "First",
        'name_last' : "Last",
    }

    user_id = requests.post(config.url + 'auth/register/v2', json=auth_register_input).json()

    dm_create_input = {
        'token' : user_id['token'],
        'u_ids' : []
    }

    dm_id = requests.post(config.url + 'dm/create/v1', json=dm_create_input).json()['dm_id']

    return {
        'valid_token_owner': user_id['token'], 
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
    timelist = []

    for _ in range (length):
        timelist.insert(0, int(datetime.utcnow().timestamp()))
        message_id_list.insert(0, requests.post(config.url + '/message/send/v1', json=send_message_input).json()['message_id'])
    
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

def test_share_channel(register_create_channel):
    new_channel_create_input = {
        'token' : register_create_channel['valid_token'],
        'name' : "new_channel",
        'is_public' : True
    }

    new_channel_id = requests.post(config.url + '/channels/create/v2', json=new_channel_create_input).json()['channel_id']

    messagedict = send_message(register_create_channel, 1)

    message_share_input = {
        'token': register_create_channel['valid_token'],
        'og_message_id': messagedict['message_id_list'][0],
        'message': "World!",
        'channel_id': new_channel_id,
        'dm_id': -1
    }

    shared_message_id = requests.post(config.url + 'message/share/v1', json=message_share_input).json()['shared_message_id']


    channel_messages_input = {
        'token' : register_create_channel['valid_token'],
        'channel_id' : new_channel_id,
        'start' : 0
    }

    channel_messages = requests.get(config.url + '/channel/messages/v2', params=channel_messages_input).json()

    assert channel_messages['messages'][0]['message_id'] == shared_message_id
    assert channel_messages['messages'][0]['u_id'] == register_create_channel['valid_user_id']
    assert channel_messages['messages'][0]['message'] == "Hello!" + "World!"
    assert abs((channel_messages['messages'][0]['time_created'] - messagedict['timelist'][0])) < 2
    assert channel_messages['messages'][0]['reacts'] == { 
                                                        'react_id': 0,
                                                        'u_ids': [],
                                                        'is_this_user_reacted': False,
                                                }
    assert channel_messages['messages'][0]['is_pinned'] == False



def test_share_dm(register_create_dm):
    new_channel_create_input = {
        'token' : register_create_dm['valid_token'],
        'name' : "new_channel",
        'is_public' : True
    }

    new_channel_id = requests.post(config.url + '/channels/create/v2', json=new_channel_create_input).json()['channel_id']

    send_message_input = {
        'token' : register_create_dm['valid_token'],
        'channel_id': new_channel_id,
        'message': "Hello!"
    }
    timesent = int(datetime.utcnow().timestamp())
    message_id = requests.post(config.url + '/message/send/v1', json=send_message_input).json()['message_id']

    message_share_input = {
        'token': register_create_dm['valid_token'],
        'og_message_id': message_id,
        'message': "World!",
        'channel_id': -1,
        'dm_id': register_create_dm['valid_dm_id']
    }

    shared_message_id = requests.post(config.url + 'message/share/v1', json=message_share_input).json()['shared_message_id']

    dm_messages_input = {
        'token' : register_create_dm['valid_token_owner'],
        'dm_id' : register_create_dm['valid_dm_id'],
        'start' : 0
    }

    dm_messages = requests.get(config.url + 'dm/messages/v1', params=dm_messages_input)

    assert dm_messages['messages'][0]['message_id'] == shared_message_id
    assert dm_messages['messages'][0]['u_id'] == register_create_channel['valid_user_id']
    assert dm_messages['messages'][0]['message'] == "Hello!" + "World!"
    assert abs((dm_messages['messages'][0]['time_created'] - timesent)) < 2
    assert dm_messages['messages'][0]['reacts'] == { 
                                                        'react_id': 0,
                                                        'u_ids': [],
                                                        'is_this_user_reacted': False,
                                                }
    assert dm_messages['messages'][0]['is_pinned'] == False

def test_invalid_channel_id_diff(register_create_channel):
    new_channel_create_input = {
        'token' : register_create_channel['valid_token'],
        'name' : "channel",
        'is_public' : True
    }

    new_channel_id = requests.post(config.url + '/channels/create/v2', json=new_channel_create_input).json()['channel_id']

    messagedict = send_message(register_create_channel, 1)

    message_share_input = {
        'token': register_create_channel['valid_token'],
        'og_message_id': messagedict['message_id_list'][0],
        'message': "World!",
        'channel_id': new_channel_id,
        'dm_id': new_channel_id + 1
    }

    status = requests.post(config.url + 'message/share/v1', json=message_share_input).json()

    assert status.status_code == InputError.code 

def test_invalid_channel_id_minus_one(register_create_channel):
    new_channel_create_input = {
        'token' : register_create_channel['valid_token'],
        'name' : "channel",
        'is_public' : True
    }

    new_channel_id = requests.post(config.url + '/channels/create/v2', json=new_channel_create_input).json()['channel_id']

    messagedict = send_message(register_create_channel, 1)

    message_share_input = {
        'token': register_create_channel['valid_token'],
        'og_message_id': messagedict['message_id_list'][0],
        'message': "World!",
        'channel_id': -1,
        'dm_id': -1
    }

    status = requests.post(config.url + 'message/share/v1', json=message_share_input).json()

    assert status.status_code == InputError.code 

def test_invalid_message_id(register_create_channel):
    new_channel_create_input = {
        'token' : register_create_channel['valid_token'],
        'name' : "channel",
        'is_public' : True
    }

    new_channel_id = requests.post(config.url + '/channels/create/v2', json=new_channel_create_input).json()['channel_id']

    messagedict = send_message(register_create_channel, 1)

    message_share_input = {
        'token': register_create_channel['valid_token'],
        'og_message_id': messagedict['message_id_list'][0] + 1,
        'message': "World!",
        'channel_id': new_channel_id,
        'dm_id': -1
    }

    status = requests.post(config.url + 'message/share/v1', json=message_share_input).json()

    assert status.status_code == InputError.code 

def test_invalid_message(register_create_channel):
    new_channel_create_input = {
        'token' : register_create_channel['valid_token'],
        'name' : "channel",
        'is_public' : True
    }

    new_channel_id = requests.post(config.url + '/channels/create/v2', json=new_channel_create_input).json()['channel_id']

    messagedict = send_message(register_create_channel, 1)

    message_share_input = {
        'token': register_create_channel['valid_token'],
        'og_message_id': messagedict['message_id_list'][0],
        'message': 'a' * 1001,
        'channel_id': new_channel_id,
        'dm_id': -1
    }

    status = requests.post(config.url + 'message/share/v1', json=message_share_input).json()

    assert status.status_code == InputError.code 

def test_invalid_token(register_create_channel):
    new_channel_create_input = {
        'token' : register_create_channel['valid_token'],
        'name' : "channel",
        'is_public' : True
    }

    new_channel_id = requests.post(config.url + '/channels/create/v2', json=new_channel_create_input).json()['channel_id']

    messagedict = send_message(register_create_channel, 1)

    message_share_input = {
        'token': " ",
        'og_message_id': messagedict['message_id_list'][0],
        'message': "Hello!",
        'channel_id': new_channel_id,
        'dm_id': -1
    }

    status = requests.post(config.url + 'message/share/v1', json=message_share_input).json()

    assert status.status_code == AccessError.code 

def test_not_member(register_create_channel):
    auth_register_input = {
        'email': "newperson@gmail.com",
        'password': "password",
        'name_first': "First",
        'name_last': "Last"
    }

    user_id = requests.post(config.url + 'auth/register/v2', json=auth_register_input).json()

    new_channel_create_input = {
        'token' : register_create_channel['valid_token'],
        'name' : "channel",
        'is_public' : True
    }

    new_channel_id = requests.post(config.url + '/channels/create/v2', json=new_channel_create_input).json()['channel_id']

    messagedict = send_message(register_create_channel, 1)

    message_share_input = {
        'token': user_id['token'],
        'og_message_id': messagedict['message_id_list'][0],
        'message': "Hello!",
        'channel_id': new_channel_id,
        'dm_id': -1
    }

    status = requests.post(config.url + 'message/share/v1', json=message_share_input).json()

    assert status.status_code == AccessError.code 










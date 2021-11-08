from requests.api import get
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
def send_message(token, channel_id, length):
    send_message_input = {
        'token' : token,
        'channel_id': channel_id,
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
# Sends a number of messages to specific endpoint
def send_messagedm(token, dm_id, length):
    send_messagedm_input = {
        'token' : token,
        'dm_id': dm_id,
        'message': "Hello!"
    }

    message_id_list = []
    timelist = []

    for _ in range (length):
        timelist.insert(0, int(datetime.utcnow().timestamp()))
        message_id_list.insert(0, requests.post(config.url + '/message/senddm/v1', json=send_messagedm_input).json()['message_id'])
    
    return {
        'timelist' : timelist,
        'message_id_list' : message_id_list
    }

# HELPER FUNCTION
# Creates input for channel_messages and returns messages
# Assumes that tests require valid input, otherwise register_create tokens/channel_ids are directly modified
def get_messages(token, channel_id, start):
    channel_messages_input = {
        'token' : token,
        'channel_id' : channel_id,
        'start' : start
    }

    channel_messages = requests.get(config.url + '/channel/messages/v2', params=channel_messages_input).json()

    return channel_messages

def test_share_channel_to_channel(register_create_channel):
    '''
    Tests sharing of message from channel to channel
    '''
    new_channel_create_input = {
        'token' : register_create_channel['valid_token'],
        'name' : "new_channel",
        'is_public' : True
    }

    new_channel_id = requests.post(config.url + '/channels/create/v2', json=new_channel_create_input).json()['channel_id']

    messagedict = send_message(register_create_channel['valid_token'], register_create_channel['valid_channel_id'], 1)

    message_share_input = {
        'token': register_create_channel['valid_token'],
        'og_message_id': messagedict['message_id_list'][0],
        'message': "World!",
        'channel_id': new_channel_id,
        'dm_id': -1
    }

    shared_message_id = requests.post(config.url + '/message/share/v1', json=message_share_input).json()['shared_message_id']

    channel_messages = get_messages(register_create_channel['valid_token'], new_channel_id, 0)

    assert channel_messages['messages'][0]['message_id'] == shared_message_id
    assert channel_messages['messages'][0]['u_id'] == register_create_channel['valid_user_id']
    assert channel_messages['messages'][0]['message'] == "World!" + "\n\n" + '"""\nHello!\n"""'
    assert abs((channel_messages['messages'][0]['time_created'] - messagedict['timelist'][0])) < 2


def test_share_channel_to_dm(register_create_dm):
    '''
    Tests sharing of message from channel to dm
    '''
    new_channel_create_input = {
        'token' : register_create_dm['valid_token'],
        'name' : "new_channel",
        'is_public' : True
    }

    new_channel_id = requests.post(config.url + '/channels/create/v2', json=new_channel_create_input).json()['channel_id']

    messagedict = send_message(register_create_dm['valid_token'], new_channel_id, 1)

    message_share_input = {
        'token': register_create_dm['valid_token'],
        'og_message_id': messagedict['message_id_list'][0],
        'message': "World!",
        'channel_id': -1,
        'dm_id': register_create_dm['valid_dm_id']
    }

    shared_message_id = requests.post(config.url + 'message/share/v1', json=message_share_input).json()['shared_message_id']

    dm_messages_input = {
        'token' : register_create_dm['valid_token'],
        'dm_id' : register_create_dm['valid_dm_id'],
        'start' : 0
    }

    dm_messages = requests.get(config.url + 'dm/messages/v1', params=dm_messages_input).json()

    assert dm_messages['messages'][0]['message_id'] == shared_message_id
    assert dm_messages['messages'][0]['u_id'] == register_create_dm['valid_user_id']
    assert dm_messages['messages'][0]['message'] == "World!" + "\n\n" + '"""\nHello!\n"""'
    assert abs((dm_messages['messages'][0]['time_created'] - messagedict['timelist'][0])) < 2

def test_share_dm_to_channel(register_create_dm):
    '''
    Tests sharing of message from dm to channel
    '''

    new_channel_create_input = {
        'token' : register_create_dm['valid_token'],
        'name' : "new_channel",
        'is_public' : True
    }

    new_channel_id = requests.post(config.url + '/channels/create/v2', json=new_channel_create_input).json()['channel_id']

    messagedict = send_messagedm(register_create_dm['valid_token'], register_create_dm['valid_dm_id'], 1)

    message_share_input = {
        'token': register_create_dm['valid_token'],
        'og_message_id': messagedict['message_id_list'][0],
        'message': "World!",
        'channel_id': new_channel_id,
        'dm_id': -1
    }

    shared_message_id = requests.post(config.url + 'message/share/v1', json=message_share_input).json()['shared_message_id']

    channel_messages = get_messages(register_create_dm['valid_token'], new_channel_id, 0)

    assert channel_messages['messages'][0]['message_id'] == shared_message_id
    assert channel_messages['messages'][0]['u_id'] == register_create_dm['valid_user_id']
    assert channel_messages['messages'][0]['message'] == "World!" + "\n\n" + '"""\nHello!\n"""'
    assert abs((channel_messages['messages'][0]['time_created'] - messagedict['timelist'][0])) < 2

def test_share_dm_to_dm(register_create_dm):
    '''
    Tests sharing of message from dm to dm
    '''
    new_dm_create_input = {
        'token' : register_create_dm['valid_token'],
        'u_ids' : []
    }

    new_dm_id = requests.post(config.url + '/dm/create/v1', json=new_dm_create_input).json()['dm_id']

    messagedict = send_messagedm(register_create_dm['valid_token'], register_create_dm['valid_dm_id'], 1)

    message_share_input = {
        'token': register_create_dm['valid_token'],
        'og_message_id': messagedict['message_id_list'][0],
        'message': "World!",
        'channel_id': -1,
        'dm_id': new_dm_id
    }

    shared_message_id = requests.post(config.url + 'message/share/v1', json=message_share_input).json()['shared_message_id']

    dm_messages_input = {
        'token' : register_create_dm['valid_token'],
        'dm_id' : new_dm_id,
        'start' : 0
    }

    dm_messages = requests.get(config.url + 'dm/messages/v1', params=dm_messages_input).json()

    assert dm_messages['messages'][0]['message_id'] == shared_message_id
    assert dm_messages['messages'][0]['u_id'] == register_create_dm['valid_user_id']
    assert dm_messages['messages'][0]['message'] == "World!" + "\n\n" + '"""\nHello!\n"""'
    assert abs((dm_messages['messages'][0]['time_created'] - messagedict['timelist'][0])) < 2


def test_invalid_channel_id_diff(register_create_channel):
    '''
    Tests where either channel id or dm id are not equal to -1
    '''
    new_channel_create_input = {
        'token' : register_create_channel['valid_token'],
        'name' : "new_channel",
        'is_public' : True
    }

    new_channel_id = requests.post(config.url + '/channels/create/v2', json=new_channel_create_input).json()['channel_id']

    messagedict = send_message(register_create_channel['valid_token'], new_channel_id, 1)

    message_share_input = {
        'token': register_create_channel['valid_token'],
        'og_message_id': messagedict['message_id_list'][0],
        'message': "World!",
        'channel_id': new_channel_id,
        'dm_id': new_channel_id + 1
    }

    status = requests.post(config.url + 'message/share/v1', json=message_share_input)

    assert status.status_code == InputError.code 


def test_invalid_channel_id_minus_one(register_create_channel):
    '''
    Tests where both channel id or dm id are equal to -1
    '''
    new_channel_create_input = {
        'token' : register_create_channel['valid_token'],
        'name' : "channel",
        'is_public' : True
    }

    new_channel_id = requests.post(config.url + '/channels/create/v2', json=new_channel_create_input).json()['channel_id']

    messagedict = send_message(register_create_channel['valid_token'], new_channel_id, 1)

    message_share_input = {
        'token': register_create_channel['valid_token'],
        'og_message_id': messagedict['message_id_list'][0],
        'message': "World!",
        'channel_id': -1,
        'dm_id': -1
    }

    status = requests.post(config.url + 'message/share/v1', json=message_share_input)

    assert status.status_code == InputError.code 

def test_invalid_channel_id(register_create_dm):
    '''
    Tests invalid channel id that does not exists
    '''

    messagedict = send_messagedm(register_create_dm['valid_token'], register_create_dm['valid_dm_id'], 1)

    message_share_input = {
        'token': register_create_dm['valid_token'],
        'og_message_id': messagedict['message_id_list'][0],
        'message': "World!",
        'channel_id': register_create_dm['valid_dm_id'] + 1,
        'dm_id': -1
    }

    status = requests.post(config.url + 'message/share/v1', json=message_share_input)

    assert status.status_code == InputError.code 

def test_invalid_dm_id(register_create_channel):
    '''
    Tests invalid channel id
    '''

    messagedict = send_message(register_create_channel['valid_token'], register_create_channel['valid_channel_id'], 1)

    message_share_input = {
        'token': register_create_channel['valid_token'],
        'og_message_id': messagedict['message_id_list'][0],
        'message': "World!",
        'channel_id': -1,
        'dm_id': register_create_channel['valid_channel_id'] + 1
    }

    status = requests.post(config.url + 'message/share/v1', json=message_share_input)

    assert status.status_code == InputError.code 


def test_invalid_message_id_shared(register_create_channel):
    '''
    Tests invalid message id that does not exist
    '''
    new_channel_create_input = {
        'token' : register_create_channel['valid_token'],
        'name' : "channel",
        'is_public' : True
    }

    new_channel_id = requests.post(config.url + '/channels/create/v2', json=new_channel_create_input).json()['channel_id']

    messagedict = send_message(register_create_channel['valid_token'], new_channel_id, 1)

    message_share_input = {
        'token': register_create_channel['valid_token'],
        'og_message_id': messagedict['message_id_list'][0] + 1,
        'message': "World!",
        'channel_id': new_channel_id,
        'dm_id': -1
    }

    status = requests.post(config.url + 'message/share/v1', json=message_share_input)

    assert status.status_code == InputError.code 

def test_invalid_message_id_og(register_create_channel):
    '''
    Tests invalid message id from og channel
    '''
    new_channel_create_input = {
        'token' : register_create_channel['valid_token'],
        'name' : "channel",
        'is_public' : True
    }

    new_channel_id = requests.post(config.url + '/channels/create/v2', json=new_channel_create_input).json()['channel_id']

    messagedict = send_message(register_create_channel['valid_token'], register_create_channel['valid_channel_id'], 1)

    auth_register_input = {
        'email': "newperson@gmail.com",
        'password': "password",
        'name_first': "First",
        'name_last': "Last"
    }

    member = requests.post(config.url + 'auth/register/v2', json=auth_register_input).json()

    channel_join_input = {
        'token' : member['token'],
        'channel_id' : new_channel_id
    }

    requests.post(config.url + '/channel/join/v2', json=channel_join_input)

    message_share_input = {
        'token': member['token'],
        'og_message_id': messagedict['message_id_list'][0],
        'message': "World!",
        'channel_id': new_channel_id,
        'dm_id': -1
    }

    status = requests.post(config.url + 'message/share/v1', json=message_share_input)

    assert status.status_code == InputError.code 

def test_invalid_message(register_create_channel):
    '''
    Tests invalid message that's too long
    '''
    new_channel_create_input = {
        'token' : register_create_channel['valid_token'],
        'name' : "channel",
        'is_public' : True
    }

    new_channel_id = requests.post(config.url + '/channels/create/v2', json=new_channel_create_input).json()['channel_id']

    messagedict = send_message(register_create_channel['valid_token'], new_channel_id, 1)

    message_share_input = {
        'token': register_create_channel['valid_token'],
        'og_message_id': messagedict['message_id_list'][0],
        'message': 'a' * 1001,
        'channel_id': new_channel_id,
        'dm_id': -1
    }

    status = requests.post(config.url + 'message/share/v1', json=message_share_input)

    assert status.status_code == InputError.code 

def test_invalid_token(register_create_channel):
    '''
    Tests invalid token
    '''
    new_channel_create_input = {
        'token' : register_create_channel['valid_token'],
        'name' : "channel",
        'is_public' : True
    }

    new_channel_id = requests.post(config.url + '/channels/create/v2', json=new_channel_create_input).json()['channel_id']

    messagedict = send_message(register_create_channel['valid_token'], new_channel_id, 1)

    message_share_input = {
        'token': " ",
        'og_message_id': messagedict['message_id_list'][0],
        'message': "Hello!",
        'channel_id': new_channel_id,
        'dm_id': -1
    }

    status = requests.post(config.url + 'message/share/v1', json=message_share_input)

    assert status.status_code == AccessError.code 

def test_not_member_shared_channel(register_create_channel):
    '''
    Tests not member of channel that message is being shared to
    '''
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

    messagedict = send_message(register_create_channel['valid_token'], new_channel_id, 1)

    message_share_input = {
        'token': user_id['token'],
        'og_message_id': messagedict['message_id_list'][0],
        'message': "Hello!",
        'channel_id': new_channel_id,
        'dm_id': -1
    }

    status = requests.post(config.url + 'message/share/v1', json=message_share_input)

    assert status.status_code == AccessError.code 










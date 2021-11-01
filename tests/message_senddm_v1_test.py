import pytest
import requests
from src import config
from src.error import AccessError, InputError

@pytest.fixture
def message_senddm_url():
    return config.url + 'message/senddm/v1'

@pytest.fixture
def clear_and_register():
    requests.delete(config.url + 'clear/v1')

    auth_register_input = {
        'email':'user@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last': 'Last'
    }
    token = requests.post(config.url + 'auth/register/v2', json=auth_register_input).json()['token']

    dms_create_input = {
        'token': token,
        'u_ids': []
    }
    dm_id = requests.post(config.url + 'dm/create/v1', json=dms_create_input).json()['dm_id']

    return {'token': token, 'dm_id': dm_id}


# Testing the general case of senddming a single message
def test_single_message(message_senddm_url, clear_and_register):
    token = clear_and_register['token']
    dm_id = clear_and_register['dm_id']

    message_senddm_input = {
        'token': token,
        'dm_id': dm_id,
        'message': "message"
    }
    requests.post(message_senddm_url, json=message_senddm_input)

    dm_messages_input = {
        'token': token,
        'dm_id': dm_id,
        'start': 0
    }
    dm_messages = requests.get(config.url + 'dm/messages/v1', params=dm_messages_input).json()['messages']
    dm_messages = [message['message'] for message in dm_messages]
    assert dm_messages == ["message"]

# Testing the case of senddming multiple messages
def test_multiple_messages(message_senddm_url, clear_and_register):
    token = clear_and_register['token']
    dm_id = clear_and_register['dm_id']

    message_senddm_input1 = {
        'token': token,
        'dm_id': dm_id,
        'message': "message1"
    }
    requests.post(message_senddm_url, json=message_senddm_input1)

    message_senddm_input2 = {
        'token': token,
        'dm_id': dm_id,
        'message': "message2"
    }
    requests.post(message_senddm_url, json=message_senddm_input2)

    dm_messages_input = {
        'token': token,
        'dm_id': dm_id,
        'start': 0
    }
    dm_messages = requests.get(config.url + 'dm/messages/v1', params=dm_messages_input).json()['messages']
    dm_messages = [message['message'] for message in dm_messages]
    assert dm_messages == ["message2", "message1"]

# Testing the error case of passing in an invalid token
def test_invalid_token(message_senddm_url, clear_and_register):
    dm_id = clear_and_register['dm_id']

    # Generating an invalid token that does not match existing tokens
    message_senddm_input = {
        'token': None,
        'dm_id': dm_id,
        'message': "message"
    }
    r = requests.post(message_senddm_url, json=message_senddm_input)

    # Throws AccessError
    assert r.status_code == AccessError.code

# Testing the error case of passing in an invalid dm_id
def test_invalid_dm_id(message_senddm_url, clear_and_register):
    token = clear_and_register['token']
    valid_dm_id = clear_and_register['dm_id']

    # Generating an invalid dm_id that does not match existing dm_ids
    invalid_dm_id = valid_dm_id + 1

    message_senddm_input = {
        'token': token,
        'dm_id': invalid_dm_id,
        'message': "message"
    }
    r = requests.post(message_senddm_url, json=message_senddm_input)

    # Throws InputError
    assert r.status_code == InputError.code

# Testing the error case of senddming a message that is too short
def test_message_too_short(message_senddm_url, clear_and_register):
    token = clear_and_register['token']
    dm_id = clear_and_register['dm_id']

    message_senddm_input = {
        'token': token,
        'dm_id': dm_id,
        'message': ""
    }
    r = requests.post(message_senddm_url, json=message_senddm_input)

    # Throws InputError
    assert r.status_code == InputError.code

# Testing the error case of senddming a message that is too long
def test_message_too_long(message_senddm_url, clear_and_register):
    token = clear_and_register['token']
    dm_id = clear_and_register['dm_id']

    message_senddm_input = {
        'token': token,
        'dm_id': dm_id,
        'message': "a" * 1001
    }
    r = requests.post(message_senddm_url, json=message_senddm_input)

    # Throws InputError
    assert r.status_code == InputError.code

# Testing the error case of passing in an invalid token, dm_id and message
def test_all_invalid_inputs(message_senddm_url, clear_and_register):
    valid_dm_id = clear_and_register['dm_id']

    # Generating an invalid token that does not match existing tokens

    # Generating an invalid dm_id that does not match existing dm_ids
    invalid_dm_id = valid_dm_id + 1

    message_senddm_input = {
        'token': None,
        'dm_id': invalid_dm_id,
        'message': "message"
    }
    r = requests.post(message_senddm_url, json=message_senddm_input)

    # Throws AccessError
    assert r.status_code == AccessError.code

# Testing the error case of senddming a message when not a member of the dm
def test_not_member_of_dm(message_senddm_url, clear_and_register):
    dm_id = clear_and_register['dm_id']
    auth_register_input = {
        'email':'new@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last': 'Last'
    }
    non_member_id = requests.post(config.url + 'auth/register/v2', json=auth_register_input).json()['token']

    message_senddm_input = {
        'token': non_member_id,
        'dm_id': dm_id,
        'message': "message"
    }
    r = requests.post(message_senddm_url, json=message_senddm_input)

    # Throws AccessError
    assert r.status_code == AccessError.code
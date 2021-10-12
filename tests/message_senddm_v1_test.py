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
    user_id = requests.post(config.url + 'auth/register/v2', json=auth_register_input).json()['auth_user_id']

    dm_create_input = {
        'token': str(user_id),
        'u_ids': []
    }
    dm_id = requests.post(config.url + 'dm/create/v1', json=dm_create_input).json()['dm_id']
    return {'user_id': user_id, 'dm_id': dm_id}

# Testing the general case of sending a single message
def test_single_message(message_senddm_url, clear_and_register):
    user_id = clear_and_register['user_id']
    dm_id = clear_and_register['dm_id']

    message_senddm_input = {
        'token': str(user_id),
        'dm_id': dm_id,
        'message': "message"
    }
    requests.post(message_senddm_url, json=message_senddm_input)

    dm_messages_input = {
        'token': str(user_id),
        'dm_id': dm_id,
        'start': 0
    }
    dm_messages = requests.get(config.url + 'dm/messages/v1', params=dm_messages_input).json()['messages']
    dm_messages = [message['message'] for message in dm_messages]
    assert dm_messages == ["message"]

# Testing the case of sending multiple messages
def test_multiple_messages(message_senddm_url, clear_and_register):
    user_id = clear_and_register['user_id']
    dm_id = clear_and_register['dm_id']

    message_senddm_input1 = {
        'token': str(user_id),
        'dm_id': dm_id,
        'message': "message1"
    }
    requests.post(message_senddm_url, json=message_senddm_input1)

    message_senddm_input2 = {
        'token': str(user_id),
        'dm_id': dm_id,
        'message': "message2"
    }
    requests.post(message_senddm_url, json=message_senddm_input2)

    dm_messages_input = {
        'token': str(user_id),
        'dm_id': dm_id,
        'start': 0
    }
    dm_messages = requests.get(config.url + 'dm/messages/v1', params=dm_messages_input).json()['messages']
    dm_messages = [message['message'] for message in dm_messages]
    assert dm_messages == ["message2", "message1"]

# Testing the error case of passing in an invalid token
def test_invalid_token(message_senddm_url, clear_and_register):
    valid_user_id = clear_and_register['user_id']
    dm_id = clear_and_register['dm_id']

    # Generating an invalid user_id that does not match existing user_ids
    invalid_user_id = valid_user_id + 1

    message_senddm_input = {
        'token': str(invalid_user_id),
        'dm_id': dm_id,
        'message': "message"
    }
    r = requests.post(message_senddm_url, json=message_senddm_input)

    # Throws AccessError
    assert r.status_code == AccessError.code

# Testing the error case of passing in an invalid dm_id
def test_invalid_dm_id(message_senddm_url, clear_and_register):
    user_id = clear_and_register['user_id']
    valid_dm_id = clear_and_register['dm_id']

    # Generating an invalid dm_id that does not match existing dm_ids
    invalid_dm_id = valid_dm_id + 1

    message_senddm_input = {
        'token': str(user_id),
        'dm_id': invalid_dm_id,
        'message': "message"
    }
    r = requests.post(message_senddm_url, json=message_senddm_input)

    # Throws InputError
    assert r.status_code == InputError.code

# Testing the error case of sending a message that is too short
def test_message_too_short(message_senddm_url, clear_and_register):
    user_id = clear_and_register['user_id']
    dm_id = clear_and_register['dm_id']

    message_senddm_input = {
        'token': str(user_id),
        'dm_id': dm_id,
        'message': ""
    }
    r = requests.post(message_senddm_url, json=message_senddm_input)

    # Throws InputError
    assert r.status_code == 400

# Testing the error case of sending a message that is too long
def test_message_too_long(message_senddm_url, clear_and_register):
    user_id = clear_and_register['user_id']
    dm_id = clear_and_register['dm_id']

    message_senddm_input = {
        'token': str(user_id),
        'dm_id': dm_id,
        'message': "a" * 1001
    }
    r = requests.post(message_senddm_url, json=message_senddm_input)

    # Throws InputError
    assert r.status_code == InputError.code

# Testing the error case of passing in an invalid token, dm_id and message
def test_all_invalid_inputs(message_senddm_url, clear_and_register):
    valid_user_id = clear_and_register['user_id']
    valid_dm_id = clear_and_register['dm_id']

    # Generating an invalid user_id that does not match existing user_ids
    invalid_user_id = valid_user_id + 1

    # Generating an invalid dm_id that does not match existing dm_ids
    invalid_dm_id = valid_dm_id + 1

    message_senddm_input = {
        'token': str(invalid_user_id),
        'dm_id': invalid_dm_id,
        'message': "message"
    }
    r = requests.post(message_senddm_url, json=message_senddm_input)

    # Throws AccessError
    assert r.status_code == AccessError.code

# Testing the error case of sending a message when not a member of the dm
def test_not_member_of_dm(message_senddm_url, clear_and_register):
    dm_id = clear_and_register['dm_id']
    auth_register_input = {
        'email':'new@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last': 'Last'
    }
    non_member_id = requests.post(config.url + 'auth/register/v2', json=auth_register_input).json()['auth_user_id']

    message_senddm_input = {
        'token': str(non_member_id),
        'dm_id': dm_id,
        'message': "message"
    }
    r = requests.post(message_senddm_url, json=message_senddm_input)

    # Throws AccessError
    assert r.status_code == AccessError.code
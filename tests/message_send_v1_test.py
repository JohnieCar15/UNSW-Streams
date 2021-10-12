import pytest
import requests
from src import config

@pytest.fixture
def message_send_url():
    return config.url + 'message/send/v1'

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

    channels_create_input = {
        'token': str(user_id),
        'u_ids': []
    }
    channel_id = requests.post(config.url + 'channels/create/v1', json=channels_create_input).json()['channel_id']
    return {'user_id': user_id, 'channel_id': channel_id}

# Testing the general case of sending a single message
def test_single_message(message_send_url, clear_and_register):
    user_id = clear_and_register['user_id']
    channel_id = clear_and_register['channel_id']

    message_send_input = {
        'token': str(user_id),
        'channel_id': channel_id,
        'message': "message"
    }
    requests.post(message_send_url, json=message_send_input)

    channel_messages_input = {
        'token': str(user_id),
        'channel_id': channel_id,
        'start': 0
    }
    channel_messages = requests.get(config.url + 'channel/messages/v2', params=channel_messages_input).json()['messages']
    channel_messages = [message['message'] for message in channel_messages]
    assert channel_messages == ["message"]

# Testing the case of sending multiple messages
def test_multiple_messages(message_send_url, clear_and_register):
    user_id = clear_and_register['user_id']
    channel_id = clear_and_register['channel_id']

    message_send_input1 = {
        'token': str(user_id),
        'channel_id': channel_id,
        'message': "message1"
    }
    requests.post(message_send_url, json=message_send_input1)

    message_send_input2 = {
        'token': str(user_id),
        'channel_id': channel_id,
        'message': "message2"
    }
    requests.post(message_send_url, json=message_send_input2)

    channel_messages_input = {
        'token': str(user_id),
        'channel_id': channel_id,
        'start': 0
    }
    channel_messages = requests.get(config.url + 'channel/messages/v2', params=channel_messages_input).json()['messages']
    channel_messages = [message['message'] for message in channel_messages]
    assert channel_messages == ["message2", "message1"]

# Testing the error case of passing in an invalid token
def test_invalid_token(message_send_url, clear_and_register):
    valid_user_id = clear_and_register['user_id']
    channel_id = clear_and_register['channel_id']

    # Generating an invalid user_id that does not match existing user_ids
    invalid_user_id = valid_user_id + 1

    message_send_input = {
        'token': str(invalid_user_id),
        'channel_id': channel_id,
        'message': "message"
    }
    r = requests.post(message_send_url, json=message_send_input)

    # Throws AccessError
    assert r.status_code == 403

# Testing the error case of passing in an invalid channel_id
def test_invalid_channel_id(message_send_url, clear_and_register):
    user_id = clear_and_register['user_id']
    valid_channel_id = clear_and_register['channel_id']

    # Generating an invalid channel_id that does not match existing channel_ids
    invalid_channel_id = valid_channel_id + 1

    message_send_input = {
        'token': str(user_id),
        'channel_id': invalid_channel_id,
        'message': "message"
    }
    r = requests.post(message_send_url, json=message_send_input)

    # Throws InputError
    assert r.status_code == 400

# Testing the error case of sending a message that is too short
def test_message_too_short(message_send_url, clear_and_register):
    user_id = clear_and_register['user_id']
    channel_id = clear_and_register['channel_id']

    message_send_input = {
        'token': str(user_id),
        'channel_id': channel_id,
        'message': ""
    }
    r = requests.post(message_send_url, json=message_send_input)

    # Throws InputError
    assert r.status_code == 400

# Testing the error case of sending a message that is too long
def test_message_too_long(message_send_url, clear_and_register):
    user_id = clear_and_register['user_id']
    channel_id = clear_and_register['channel_id']

    message_send_input = {
        'token': str(user_id),
        'channel_id': channel_id,
        'message': "a" * 1001
    }
    r = requests.post(message_send_url, json=message_send_input)

    # Throws InputError
    assert r.status_code == 400

# Testing the error case of passing in an invalid token, channel_id and message
def test_all_invalid_inputs(message_send_url, clear_and_register):
    valid_user_id = clear_and_register['user_id']
    valid_channel_id = clear_and_register['channel_id']

    # Generating an invalid user_id that does not match existing user_ids
    invalid_user_id = valid_user_id + 1

    # Generating an invalid channel_id that does not match existing channel_ids
    invalid_channel_id = valid_channel_id + 1

    message_send_input = {
        'token': str(invalid_user_id),
        'channel_id': invalid_channel_id,
        'message': "message"
    }
    r = requests.post(message_send_url, json=message_send_input)

    # Throws AccessError
    assert r.status_code == 403

# Testing the error case of sending a message when not a member of the channel
def test_not_member_of_channel(message_send_url, clear_and_register):
    channel_id = clear_and_register['channel_id']
    auth_register_input = {
        'email':'new@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last': 'Last'
    }
    non_member_id = requests.post(config.url + 'auth/register/v2', json=auth_register_input).json()['auth_user_id']

    message_send_input = {
        'token': str(non_member_id),
        'channel_id': channel_id,
        'message': "message"
    }
    r = requests.post(message_send_url, json=message_send_input)

    # Throws AccessError
    assert r.status_code == 403
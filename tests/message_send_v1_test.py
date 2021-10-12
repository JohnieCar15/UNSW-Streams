import pytest

from src.message import message_send_v1
from src.channel import channel_join_v1, channel_messages_v1
from src.channels import channels_create_v1
from src.auth import auth_register_v1
from src.other import clear_v1
from src.error import InputError, AccessError

def test_normal():
    clear_v1()
    user_info = auth_register_v1("registered@gmail.com", "password", "First", "Last")
    user_token = user_info['token']
    user_id = user_info['auth_user_id']
    
    channel_id = channels_create_v1(user_token, "name", True)
    channel_join_v1(user_token, channel_id)

    message_id = message_send_v1(user_token, channel_id, "Hello!")['message_id']

    assert(channel_messages_v1(user_token, channel_id, 0)) == {
        'messages' == [{'message_id': message_id, 'u_id': user_id, 'message': "Hello!", 'time_created': 1200}],
        'start' == 0,
        'end' == 1,
    }

def test_multiple_messages():
    clear_v1()
    user_info = auth_register_v1("registered@gmail.com", "password", "First", "Last")
    user_token = user_info['token']
    user_id = user_info['auth_user_id']
    
    channel_id = channels_create_v1(user_token, "name", True)
    channel_join_v1(user_token, channel_id)

    message_id = message_send_v1(user_token, channel_id, "Hello!")['message_id']


    message_id2 = message_send_v1(user_token, channel_id, "World!")['message_id']

    assert(channel_messages_v1(user_token, channel_id, 0)) == {
        'messages' == [{'message_id': message_id, 'u_id': user_id, 'message': "Hello!", 'time_created': 1200},
        {'message_id': message_id2, 'message': "World!", 'time_created': 1200}],
        'start' == 0,
        'end' == 2,
    }

def test_invalid_channel_id():
    clear_v1()
    user_info = auth_register_v1("registered@gmail.com", "password", "First", "Last")
    user_token = user_info['token']
    user_id = user_info['auth_user_id']

    with pytest.raises(InputError):
        message_id = message_send_v1(user_token, 0, "Hello!")['message_id']

def test_invalid_message():
    clear_v1()
    user_info = auth_register_v1("registered@gmail.com", "password", "First", "Last")
    user_token = user_info['token']
    user_id = user_info['auth_user_id']
    
    channel_id = channels_create_v1(user_token, "name", True)
    channel_join_v1(user_token, channel_id)

    with pytest.raises(InputError):
        message_id = message_send_v1(user_token, channel_id, "")['message_id']

def test_invalid_message():
    clear_v1()
    user_info = auth_register_v1("registered@gmail.com", "password", "First", "Last")
    user_token = user_info['token']
    user_id = user_info['auth_user_id']
    
    channel_id = channels_create_v1(user_token, "name", True)
    channel_join_v1(user_token, channel_id)

    with pytest.raises(InputError):
        message_id = message_send_v1(user_token, channel_id, 'a' * 1000)['message_id']

def test_invalid_user_valid_message():
    clear_v1()
    user_info = auth_register_v1("registered@gmail.com", "password", "First", "Last")
    user_token = user_info['token']
    user_id = user_info['auth_user_id']
    
    channel_id = channels_create_v1(user_token, "name", True)

    with pytest.raises(AccessError):
        message_id = message_send_v1(user_token, channel_id, "Hello!")['message_id']

def test_invalid_user_invalid_message():
    clear_v1()
    user_info = auth_register_v1("registered@gmail.com", "password", "First", "Last")
    user_token = user_info['token']
    user_id = user_info['auth_user_id']
    
    channel_id = channels_create_v1(user_token, "name", True)

    with pytest.raises(AccessError):
        message_id = message_send_v1(user_token, channel_id, "")['message_id']



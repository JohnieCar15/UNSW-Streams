import pytest

from src.channel import channel_messages_v1
from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.other import clear_v1
from src.error import InputError, AccessError

# Under the assumption that messages cannot be added so the messages datastore remains empty

def test_normal():
    clear_v1()
    valid_user_id = auth_register_v1("valid@gmail.com", "password", "First", "Last")
    valid_channel_id = channels_create_v1(valid_user_id, "channel", True)

    assert(channel_messages_v1(valid_user_id, valid_channel_id, 0)) == {
        'messages': [{}],
        'start': 0,
        'end': -1
    }

def test_invalid_start():
    clear_v1()
    valid_user_id = auth_register_v1("valid@gmail.com", "password", "First", "Last")
    valid_channel_id = channels_create_v1(valid_user_id, "channel", True)

    with pytest.raises(InputError):
        assert(channel_messages_v1(valid_user_id, valid_channel_id, 10))

def test_invalid_channel_id():
    clear_v1()
    valid_user_id = auth_register_v1("valid@gmail.com", "password", "First", "Last")

    with pytest.raises(InputError):
        assert(channel_messages_v1(valid_user_id, 10, 0))

def test_invalid_user_id():
    clear_v1()
    valid_user_id = auth_register_v1("valid@gmail.com", "password", "First", "Last")
    valid_channel_id = channels_create_v1(valid_user_id, "channel", True)

    with pytest.raises(AccessError):
        assert(channel_messages_v1(valid_user_id + 1, valid_channel_id, 0))

def test_invalid_channel_id_invalid_user_id():
    clear_v1()
    with pytest.raises(AccessError):
        assert(channel_messages_v1(10, 10, 0))

def test_invalid_start_invalid_id():
    clear_v1()
    valid_user_id = auth_register_v1("valid@gmail.com", "password", "First", "Last")
    valid_channel_id = channels_create_v1(valid_user_id, "channel", True)

    with pytest.raises(AccessError):
        assert(channel_messages_v1(valid_user_id + 1, valid_channel_id, 10))

def test_invalid_start_invalid_channel():
    clear_v1()
    valid_user_id = auth_register_v1("valid@gmail.com", "password", "First", "Last")

    with pytest.raises(InputError):
        assert(channel_messages_v1(valid_user_id, 10, 10))








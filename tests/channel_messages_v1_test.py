import pytest

from src.channel import channel_messages_v1
from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.other import clear_v1
from src.error import InputError, AccessError

# Under the assumption that messages cannot be added so the messages datastore remains empty
# Note: When clear_v1() is run, the data store is empty so all ids passed will be invalid

# Tests the normal functionality of channels_message_v1
def test_normal():
    clear_v1()
    valid_user_id = auth_register_v1("valid@gmail.com", "password", "First", "Last")['auth_user_id']
    valid_channel_id = channels_create_v1(valid_user_id, "channel", True)['channel_id']

    assert(channel_messages_v1(valid_user_id, valid_channel_id, 0)) == {
        'messages': [],
        'start': 0,
        'end': -1
    }

# Tests invalid start
def test_invalid_start():
    clear_v1()
    valid_user_id = auth_register_v1("valid@gmail.com", "password", "First", "Last")['auth_user_id']
    valid_channel_id = channels_create_v1(valid_user_id, "channel", True)['channel_id']

    with pytest.raises(InputError):
        channel_messages_v1(valid_user_id, valid_channel_id, 10)

# Tests invalid channel id and valid user id
def test_invalid_channel_id():
    clear_v1()
    valid_user_id = auth_register_v1("valid@gmail.com", "password", "First", "Last")['auth_user_id']

    with pytest.raises(InputError):
        channel_messages_v1(valid_user_id, 10, 0)

# Tests valid channel id and invalid user id
def test_invalid_user_id():
    clear_v1()
    valid_user_id = auth_register_v1("valid@gmail.com", "password", "First", "Last")['auth_user_id']
    valid_channel_id = channels_create_v1(valid_user_id, "channel", True)['channel_id']

    with pytest.raises(AccessError):
        channel_messages_v1(valid_user_id + 1, valid_channel_id, 0)

# Tests invalid start and invalid user id
def test_invalid_start_invalid_id():
    clear_v1()
    valid_user_id = auth_register_v1("valid@gmail.com", "password", "First", "Last")['auth_user_id']
    valid_channel_id = channels_create_v1(valid_user_id, "channel", True)['channel_id']

    with pytest.raises(AccessError):
        channel_messages_v1(valid_user_id + 1, valid_channel_id, 10)

# Tests invalid start and invalid channel id
def test_invalid_start_invalid_channel():
    clear_v1()
    valid_user_id = auth_register_v1("valid@gmail.com", "password", "First", "Last")['auth_user_id']

    with pytest.raises(InputError):
        channel_messages_v1(valid_user_id, 10, 10)








import pytest

from src.channel import channel_messages_v1
from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.other import clear_v1
from src.error import InputError, AccessError

# Under the assumption that messages cannot be added so the messages datastore remains empty
# Note: When clear_v1() is run, the data store is empty so all ids passed will be invalid

@pytest.fixture
def register_create():
    clear_v1()
    user_id = auth_register_v1("valid@gmail.com", "password", "First", "Last")['auth_user_id']
    channel_id = channels_create_v1(user_id, "channel", True)['channel_id']
    return {'valid_user_id': user_id, 'valid_channel_id': channel_id}


# Tests the normal functionality of channels_message_v1
def test_normal(register_create):
    assert(channel_messages_v1(register_create['valid_user_id'], register_create['valid_channel_id'], 0)) == {
        'messages': [],
        'start': 0,
        'end': -1
    }

# Tests invalid start
def test_invalid_start(register_create):
    with pytest.raises(InputError):
        channel_messages_v1(register_create['valid_user_id'], register_create['valid_channel_id'], 10)

# Tests invalid channel id and valid user id
def test_invalid_channel_id(register_create):
    with pytest.raises(InputError):
        channel_messages_v1(register_create['valid_user_id'], register_create['valid_channel_id'] + 1, 0)

# Tests valid channel id and invalid user id
def test_invalid_user_id(register_create):
    with pytest.raises(AccessError):
        channel_messages_v1(register_create['valid_user_id'] + 1, register_create['valid_channel_id'], 0)

# Tests invalid start and invalid user id
def test_invalid_start_invalid_id(register_create):
    with pytest.raises(AccessError):
        channel_messages_v1(register_create['valid_user_id'] + 1, register_create['valid_channel_id'], 10)

# Tests invalid start and invalid channel id
def test_invalid_start_invalid_channel(register_create):
    with pytest.raises(InputError):
        channel_messages_v1(register_create['valid_user_id'], register_create['valid_channel_id'] + 1, 10)








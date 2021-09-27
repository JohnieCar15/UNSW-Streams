import pytest

from src.other import clear_v1
from src.auth import auth_register_v1, auth_login_v1
from src.channels import channels_create_v1
from src.channel import channel_details_v1, channel_join_v1, channel_messages_v1
from src.error import InputError

'''
@pytest.fixture
def user_id():
    userid = auth_register_v1("valid@gmail.com", "password", "First", "Last")
    return userid

@pytest.fixture
def channel_id():
    channelid = channels_create_v1(user_id, "channel", True)
    return channelid
'''

def test_register_login():
    auth_register_v1("valid@gmail.com", "password", "First", "Last")
    clear_v1()
    
    with pytest.raises(InputError):
        assert(auth_login_v1("valid@gmail.com", "password"))

def test_register_twice():
    auth_register_v1("valid@gmail.com", "password", "First", "Last")
    clear_v1()
    auth_register_v1("valid@gmail.com", "password", "First", "Last")

def test_channel_details():
    user_id = auth_register_v1("valid@gmail.com", "password", "First", "Last")
    channel_id = channels_create_v1(user_id, "channel", True)

    clear_v1()
    with pytest.raises(InputError):
        assert(channel_details_v1(user_id, channel_id))

def test_channel_join():
    user_id = auth_register_v1("valid@gmail.com", "password", "First", "Last")
    channel_id = channels_create_v1(user_id, "channel", True)

    clear_v1()
    with pytest.raises(InputError):
        assert(channel_join_v1(user_id, channel_id))

def test_channel_message():
    user_id = auth_register_v1("valid@gmail.com", "password", "First", "Last")
    channel_id = channels_create_v1(user_id, "channel", True)

    clear_v1()
    with pytest.raises(InputError):
        assert(channel_messages_v1(user_id, channel_id, 0))



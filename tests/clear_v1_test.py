import pytest

from src.other import clear_v1
from src.auth import auth_register_v1, auth_login_v1
from src.channels import channels_create_v1
from src.channel import channel_details_v1, channel_join_v1, channel_messages_v1
from src.error import InputError

# Tests logging in after clearing data store
def test_register_login():
    clear_v1()
    auth_register_v1("valid@gmail.com", "password", "First", "Last")
    clear_v1()
    
    with pytest.raises(InputError):
        auth_login_v1("valid@gmail.com", "password")

# Tests if registering again after clearing works
def test_register_twice():
    clear_v1()
    auth_register_v1("valid@gmail.com", "password", "First", "Last")
    clear_v1()
    auth_register_v1("valid@gmail.com", "password", "First", "Last")

# Tests checking channel details after clearing data store
def test_channel_details():
    clear_v1()
    user_id = auth_register_v1("valid@gmail.com", "password", "First", "Last")['auth_user_id']
    channel_id = channels_create_v1(user_id, "channel", True)['channel_id']

    clear_v1()
    user_id_2 = auth_register_v1("valid@gmail.com", "password", "First", "Last")['auth_user_id']
    with pytest.raises(InputError):
        channel_details_v1(user_id_2, channel_id)

# Tests checking channel joining after clearing data store
def test_channel_join():
    clear_v1()
    user_id = auth_register_v1("valid@gmail.com", "password", "First", "Last")['auth_user_id']
    channel_id = channels_create_v1(user_id, "channel", True)['channel_id']

    clear_v1()
    user_id_2 = auth_register_v1("valid@gmail.com", "password", "First", "Last")['auth_user_id']
    with pytest.raises(InputError):
        channel_join_v1(user_id_2, channel_id)

# Tests checking channel messages after clearing data store
def test_channel_message():
    clear_v1()
    user_id = auth_register_v1("valid@gmail.com", "password", "First", "Last")['auth_user_id']
    channel_id = channels_create_v1(user_id, "channel", True)['channel_id']

    clear_v1()
    user_id_2 = auth_register_v1("valid@gmail.com", "password", "First", "Last")['auth_user_id']
    with pytest.raises(InputError):
        channel_messages_v1(user_id_2, channel_id, 0)


import pytest

from src.auth import auth_register_v1, auth_login_v1
from src.channel import channel_details_v1
from src.channels import channels_create_v1
from src.other import clear_v1
from src.error import InputError

@pytest.fixture
def clear():
    clear_v1()

def test_auth_register_v1(clear):
    register_return = auth_register_v1("valid@gmail.com", "password", "First", "Last")
    register_auth_user_id = register_return['auth_user_id']

    login_return = auth_login_v1("valid@gmail.com", "password")
    login_auth_user_id = login_return['auth_user_id']

    assert register_auth_user_id == login_auth_user_id

def test_invalid_email(clear):
    with pytest.raises(InputError):
        auth_register_v1("invalidemail", "password", "First", "Last")

def test_registered_email(clear):
    auth_register_v1("valid@gmail.com", "password", "First", "Last")
    
    with pytest.raises(InputError):
        auth_register_v1("valid@gmail.com", "password1", "First1", "Last1")

def test_short_password(clear):
    with pytest.raises(InputError):
        auth_register_v1("valid@gmail.com", "pass", "First", "Last")

def test_short_firstname(clear):
    with pytest.raises(InputError):
        auth_register_v1("valid@gmail.com", "password", "", "Last")

def test_long_firstname(clear):
    with pytest.raises(InputError):
        auth_register_v1("valid@gmail.com", "password", ("a" * 51), "Last")

def test_short_lastname(clear):
    with pytest.raises(InputError):
        auth_register_v1("valid@gmail.com", "password", "First", "")

def test_long_lastname(clear): 
    with pytest.raises(InputError):
        auth_register_v1("valid@gmail.com", "password", "First", ("a" * 51))

def test_no_alphanumeric_characters(clear):
    with pytest.raises(InputError):
        auth_register_v1("valid@gmail.com", "password", "@#!$!", "@$#!$*")

def test_handle(clear):
    auth_user_id = auth_register_v1("valid@gmail.com", "password", "First", "Last")['auth_user_id']

    channel_id = channels_create_v1(auth_user_id, "channel", True)['channel_id']

    handle = channel_details_v1(auth_user_id, channel_id)['all_members'][0]['handle_str']

    assert handle == "firstlast"

def test_handle_numeric(clear):
    auth_user_id = auth_register_v1("valid@gmail.com", "password", "12345", "12345")['auth_user_id']

    channel_id = channels_create_v1(auth_user_id, "channel", True)['channel_id']

    handle = channel_details_v1(auth_user_id, channel_id)['all_members'][0]['handle_str']

    assert handle == "1234512345"

def test_handle_uppercase(clear):
    auth_user_id = auth_register_v1("valid@gmail.com", "password", "FIRST", "LAST")['auth_user_id']

    channel_id = channels_create_v1(auth_user_id, "channel", True)['channel_id']

    handle = channel_details_v1(auth_user_id, channel_id)['all_members'][0]['handle_str']

    assert handle == "firstlast"

def test_double_handles(clear):
    auth_register_v1("valid@gmail.com", "password", "First", "Last")['auth_user_id']

    auth_user_id = auth_register_v1("other@gmail.com", "password", "First", "Last")['auth_user_id']

    channel_id = channels_create_v1(auth_user_id, "channel", True)['channel_id']

    handle = channel_details_v1(auth_user_id, channel_id)['all_members'][0]['handle_str']

    assert handle == "firstlast0"

def test_multiple_handles(clear):
    auth_register_v1("valid@gmail.com", "password", "First", "Last")['auth_user_id']
    auth_register_v1("other@gmail.com", "password", "First", "Last")['auth_user_id']

    auth_user_id = auth_register_v1("final@gmail.com", "password", "First", "Last")['auth_user_id']

    channel_id = channels_create_v1(auth_user_id, "channel", True)['channel_id']

    handle = channel_details_v1(auth_user_id, channel_id)['all_members'][0]['handle_str']

    assert handle == "firstlast1"

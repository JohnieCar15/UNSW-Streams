import pytest

from src.auth import auth_register_v1, auth_login_v1
from src.channel import channel_details_v1
from src.channels import channels_create_v1
from src.other import clear_v1
from src.error import InputError

@pytest.fixture
def clear():
    clear_v1()

# Test if function works when given correct input
def test_auth_register_v1(clear):
    register_return = auth_register_v1("valid@gmail.com", "password", "First", "Last")
    register_auth_user_id = register_return['auth_user_id']

    login_return = auth_login_v1("valid@gmail.com", "password")
    login_auth_user_id = login_return['auth_user_id']

    assert register_auth_user_id == login_auth_user_id

# Test if function is given an invalid email
def test_invalid_email(clear):
    with pytest.raises(InputError):
        auth_register_v1("invalidemail", "password", "First", "Last")

# Test if function is given an email that has already been registered
def test_registered_email(clear):
    auth_register_v1("valid@gmail.com", "password", "First", "Last")
    
    with pytest.raises(InputError):
        auth_register_v1("valid@gmail.com", "password1", "First1", "Last1")

# Test if function is given a password < 6 chracters
def test_short_password(clear):
    with pytest.raises(InputError):
        auth_register_v1("valid@gmail.com", "pass", "First", "Last")

# Test if function is given a first name < 1 character
def test_short_firstname(clear):
    with pytest.raises(InputError):
        auth_register_v1("valid@gmail.com", "password", "", "Last")

# Test if function is given a first name > 50 characters
def test_long_firstname(clear):
    with pytest.raises(InputError):
        auth_register_v1("valid@gmail.com", "password", ("a" * 51), "Last")

# Test if function is given a last name < 1 character
def test_short_lastname(clear):
    with pytest.raises(InputError):
        auth_register_v1("valid@gmail.com", "password", "First", "")

# Test if function is given a last name > 50 characters
def test_long_lastname(clear): 
    with pytest.raises(InputError):
        auth_register_v1("valid@gmail.com", "password", "First", ("a" * 51))

# Test if function is given a first name and last name that do not contain alphanumeric characters
def test_no_alphanumeric_characters(clear):
    with pytest.raises(InputError):
        auth_register_v1("valid@gmail.com", "password", "@#!$!", "@$#!$*")

# Test if function generates correct handle
def test_handle(clear):
    auth_user_id = auth_register_v1("valid@gmail.com", "password", "First", "Last")['auth_user_id']

    channel_id = channels_create_v1(auth_user_id, "channel", True)['channel_id']

    handle = channel_details_v1(auth_user_id, channel_id)['all_members'][0]['handle_str']

    assert handle == "firstlast"

# Test if function generates correct handle when given numeric first and last names
def test_handle_numeric(clear):
    auth_user_id = auth_register_v1("valid@gmail.com", "password", "12345", "12345")['auth_user_id']

    channel_id = channels_create_v1(auth_user_id, "channel", True)['channel_id']

    handle = channel_details_v1(auth_user_id, channel_id)['all_members'][0]['handle_str']

    assert handle == "1234512345"

# Test if function generates correct handle when given uppercase first an last names
def test_handle_uppercase(clear):
    auth_user_id = auth_register_v1("valid@gmail.com", "password", "FIRST", "LAST")['auth_user_id']

    channel_id = channels_create_v1(auth_user_id, "channel", True)['channel_id']

    handle = channel_details_v1(auth_user_id, channel_id)['all_members'][0]['handle_str']

    assert handle == "firstlast"

# Test if function generates correct handle when the same handle already exists
def test_double_handles(clear):
    auth_register_v1("valid@gmail.com", "password", "First", "Last")['auth_user_id']

    auth_user_id = auth_register_v1("other@gmail.com", "password", "First", "Last")['auth_user_id']

    channel_id = channels_create_v1(auth_user_id, "channel", True)['channel_id']

    handle = channel_details_v1(auth_user_id, channel_id)['all_members'][0]['handle_str']

    assert handle == "firstlast0"

# Test if function generates correct handle if multiple of the same handle already exist
def test_multiple_handles(clear):
    auth_register_v1("valid@gmail.com", "password", "First", "Last")['auth_user_id']
    auth_register_v1("other@gmail.com", "password", "First", "Last")['auth_user_id']

    auth_user_id = auth_register_v1("final@gmail.com", "password", "First", "Last")['auth_user_id']

    channel_id = channels_create_v1(auth_user_id, "channel", True)['channel_id']

    handle = channel_details_v1(auth_user_id, channel_id)['all_members'][0]['handle_str']

    assert handle == "firstlast1"

# Test if function generates handle firstlast00 when given name_first: first, name_last: last0, and firstlast0 already exists
def test_numeric_last_char(clear):
    auth_register_v1("valid@gmail.com", "password", "First", "Last")
    auth_register_v1("other@gmail.com", "password", "First", "Last")

    auth_user_id = auth_register_v1("final@gmail.com", "password", "First", "Last0")['auth_user_id']

    channel_id = channels_create_v1(auth_user_id, "channel", True)['channel_id']

    handle = channel_details_v1(auth_user_id, channel_id)['all_members'][0]['handle_str']

    assert handle == "firstlast00"

# Test if function generates correct handle when more than 10 of the same handle exist
def test_13_duplicate_handles(clear):
    auth_register_v1("valid@gmail.com", "password", "First", "Last")
    for i in range(11):
        email = str(i) + "@gmail.com"
        auth_register_v1(email, "password", "First", "Last")

    auth_user_id = auth_register_v1("11@gmail.com", "password", "First", "Last")['auth_user_id']

    channel_id = channels_create_v1(auth_user_id, "channel", True)['channel_id']

    handle = channel_details_v1(auth_user_id, channel_id)['all_members'][0]['handle_str']

    assert handle == "firstlast11"

import pytest

from src.auth import auth_register_v1
from src.auth import auth_login_v1
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
        assert auth_register_v1("invalidemail", "password", "First", "Last")

def test_registered_email(clear):
    auth_register_v1("valid@gmail.com", "password", "First", "Last")
    
    with pytest.raises(InputError):
        assert auth_register_v1("valid@gmail.com", "password1", "First1", "Last1")

def test_short_password(clear):
    with pytest.raises(InputError):
        assert auth_register_v1("valid@gmail.com", "pass", "First", "Last")

def test_short_firstname(clear):
    with pytest.raises(InputError):
        assert auth_register_v1("valid@gmail.com", "password", "", "Last")

def test_long_firstname(clear):
    with pytest.raises(InputError):
        assert auth_register_v1("valid@gmail.com", "password", ("a" * 51), "Last")

def test_short_lastname(clear):
    with pytest.raises(InputError):
        assert auth_register_v1("valid@gmail.com", "password", "First", "")

def test_long_lastname(clear): 
    with pytest.raises(InputError):
        assert auth_register_v1("valid@gmail.com", "password", "First", ("a" * 51))

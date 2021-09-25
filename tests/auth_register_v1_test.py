import pytest

from src.auth import auth_register_v1
from src.other import clear_v1
from src.error import InputError

def test_auth_register_v1():
    clear_v1()

    assert auth_register_v1("valid@gmail.com", "password", "First", "Last") == 0

def test_invalid_email():
    with pytest.raises(InputError):
        assert auth_register_v1("invalidemail", "password", "First", "Last")

def test_registered_email():
    assert auth_register_v1("valid@gmail.com", "password", "First", "Last")
    with pytest.raises(InputError):
        assert auth_register_v1("valid@gmail.com", "password1", "First1", "Last1")

def test_short_password():
    with pytest.raises(InputError):
        assert auth_register_v1("valid@gmail.com", "pass", "First", "Last")

def test_short_firstname():
    with pytest.raises(InputError):
        assert auth_register_v1("valid@gmail.com", "password", "", "Last")

def test_long_firstname():
    with pytest.raises(InputError):
        assert auth_register_v1("valid@gmail.com", "password", ("a" * 51), "Last")

def test_short_lastname():
    with pytest.raises(InputError):
        assert auth_register_v1("valid@gmail.com", "password", "First", "")

def test_long_lastname():
    with pytest.raises(InputError):
        assert auth_register_v1("valid@gmail.com", "password", "First", ("a" * 51))

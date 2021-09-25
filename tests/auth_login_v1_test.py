import pytest

from src.auth import auth_login_v1
from src.auth import auth_register_v1
from src.other import clear_v1
from src.error import InputError

def test_auth_login_v1():
    clear_v1()
    auth_register_v1("valid@gmail.com", "password", "First", "Last")

    assert auth_login_v1("valid@gmail.com", "password") == 0

def test_unregistered_email():
    clear_v1()

    with pytest.raises(InputError):
        assert auth_login_v1("unregistered@gmail.com", "password")
    
def test_incorrect_password():
    clear_v1()
    auth_register_v1("valid@gmail.com", "password", "First", "Last")

    with pytest.raises(InputError):
        assert auth_login_v1("valid@gmail.com", "notpassword")
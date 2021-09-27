import pytest

from src.auth import auth_login_v1
from src.auth import auth_register_v1
from src.other import clear_v1
from src.error import InputError

@pytest.fixture
def clear():
    clear_v1()

def test_auth_login_v1(clear):
    register_return = auth_register_v1("valid@gmail.com", "password", "First", "Last")
    register_auth_user_id = register_return['auth_user_id']

    login_return = auth_login_v1("valid@gmail.com", "password")
    login_auth_user_id = login_return['auth_user_id']

    assert register_auth_user_id == login_auth_user_id

def test_unregistered_email(clear):
    with pytest.raises(InputError):
        assert auth_login_v1("unregistered@gmail.com", "password")
    
def test_incorrect_password(clear):
    auth_register_v1("valid@gmail.com", "password", "First", "Last")

    with pytest.raises(InputError):
        assert auth_login_v1("valid@gmail.com", "notpassword")
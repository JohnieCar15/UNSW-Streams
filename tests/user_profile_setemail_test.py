import pytest
import requests
from src import config
from src.error import AccessError, InputError

# assumption: when token and email are valid, but the email
# entered by the user is same with previous email, InputError will be raised


# clear and registers first user
@pytest.fixture
def clear_and_register_user0():
    requests.delete(config.url + 'clear/v2')
    user0_register = {
        "email" : "0000@unsw.edu.au",
        "password" : "password",
        "name_first" : "firstname0",
        "name_last" : "lastname0",
    }
    user0 = requests.post(config.url + 'auth/register/v2', json=user0_register).json()

    user2_register = {
        "email" : "0002@unsw.edu.au",
        "password" : "password",
        "name_first" : "firstname2",
        "name_last" : "lastname2",
    }
    requests.post(config.url + 'auth/register/v2', json=user2_register).json()
    return {
        "token": user0['token'],
        "u_id": user0['auth_user_id']
    }


# test invalid token with valid email, this should raise AccessError
def test_invalid_token_and_valid_email(clear_and_register_user0):
    user0 = clear_and_register_user0
    input = {
        "token": user0['token'] + "1",
        "email": "0001@unsw.edu.au"
    }
    assert requests.put(config.url + 'user/profile/setemail/v1', json=input).status_code == AccessError.code


# test invalid token with invalid email, this should raise AccessError
def test_invalid_token_and_invalid_email(clear_and_register_user0):
    user0 = clear_and_register_user0
    input = {
        "token": user0['token'] + "1",
        "email": "unsw.edu.au"
    }
    assert requests.put(config.url + 'user/profile/setemail/v1', json=input).status_code == AccessError.code


# test valid token with invalid email, this should raise InputError
def test_valid_token_and_invalid_email(clear_and_register_user0):
    user0 = clear_and_register_user0
    input = {
        "token": user0['token'],
        "email": "unsw.edu.au"
    }
    assert requests.put(config.url + 'user/profile/setemail/v1', json=input).status_code == InputError.code


# test valid token and email, but the email is used by others, this should raise InputError
def test_email_used_by_others(clear_and_register_user0):
    clear_and_register_user0
    user1_register = {
        "email" : "0001@unsw.edu.au",
        "password" : "password",
        "name_first" : "firstname1",
        "name_last" : "lastname1",
    }
    user1 = requests.post(config.url + 'auth/register/v2', json=user1_register).json()
    input = {
        "token": user1['token'],
        "email": "0000@unsw.edu.au"
    }
    assert requests.put(config.url + 'user/profile/setemail/v1', json=input).status_code == InputError.code

# test valid token and email, the email is the same as previous, this should raise InputError
def test_same_email_as_previous(clear_and_register_user0):
    user0 = clear_and_register_user0
    input = {
        "token": user0['token'],
        "email": "0000@unsw.edu.au"
    }
    assert requests.put(config.url + 'user/profile/setemail/v1', json=input).status_code == InputError.code

# test valid token with valid name
def test_valid_token_and_valid_email(clear_and_register_user0):
    user0 = clear_and_register_user0
    input = {
        "token": user0['token'],
        "email": "0001@unsw.edu.au"
    }
    requests.put(config.url + 'user/profile/setemail/v1', json=input)
    input = {
        "token": user0['token'],
        "u_id": user0['u_id']
    }
    assert requests.get(config.url + 'user/profile/v1', params=input).json()["user"]["email"] == "0001@unsw.edu.au"

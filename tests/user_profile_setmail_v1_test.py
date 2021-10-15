import pytest
import requests
from src import config
from src.error import AccessError, InputError


# assumption: when token and mail are valid, but the mail
# entered by the user is same with previous mail, InputError will be raised


# clear and registers first user
@pytest.fixture
def clear_and_register_user0():
    requests.delete(config.url + '/clear/v2')
    user0_register = {
        "email" : "0000@unsw.edu.au",
        "password" : "password",
        "name_first" : "firstname0",
        "name_last" : "lastname0",
    }
    user0 = requests.post(config.url + '/auth/register/v2', data=user0_register).json()
    return {
        "token": user0['token'],
        "u_id": user0['auth_user_id']
    }

# test invalid token with valid mail, this should raise AccessError
def test_invalid_token_and_valid_mail(clear_and_register_user0):
    user0 = clear_and_register_user0
    input = {
        "token": user0['token'] + "1",
        "mail": "0001@unsw.edu.au"
    }
    assert requests.put(config.url + '/user/profile/setmail/v1/', data=input).status_code == AccessError.code

# test invalid token with invalid mail, this should raise AccessError
def test_invalid_token_and_invalid_mail(clear_and_register_user0):
    user0 = clear_and_register_user0
    input = {
        "token": user0['token'] + "1",
        "mail": "unsw.edu.au"
    }
    assert requests.put(config.url + '/user/profile/setmail/v1/', data=input).status_code == AccessError.code


# test valid token with invalid mail, this should raise InputError
def test_valid_token_and_invalid_mail(clear_and_register_user0):
    user0 = clear_and_register_user0
    input = {
        "token": user0['token'],
        "mail": "unsw.edu.au"
    }
    assert requests.put(config.url + '/user/profile/setmail/v1/', data=input).status_code == InputError.code


# test valid token and mail, but the mail is used by others, this should raise InputError
def test_mail_used_by_others(clear_and_register_user0):
    clear_and_register_user0
    user1_register = {
        "email" : "0001@unsw.edu.au",
        "password" : "password",
        "name_first" : "firstname1",
        "name_last" : "lastname1",
    }
    user1 = requests.post(config.url + '/auth/register/v2', data=user1_register).json()
    input = {
        "token": user1['token'],
        "mail": "0000@unsw.edu.au"
    }
    assert requests.put(config.url + '/user/profile/setmail/v1/', data=input).status_code == InputError.code

# test valid token and mail, the mail is the same as previous, this should raise InputError
def test_same_mail_as_previous(clear_and_register_user0):
    user0 = clear_and_register_user0
    input = {
        "token": user0['token'],
        "mail": "0000@unsw.edu.au"
    }
    assert requests.put(config.url + '/user/profile/setmail/v1/', data=input).status_code == InputError.code

# test valid token with valid name
def test_valid_token_and_valid_mail(clear_and_register_user0):
    user0 = clear_and_register_user0
    input = {
        "token": user0['token'],
        "mail": "0001@unsw.edu.au"
    }
    requests.put(config.url + '/user/profile/setmail/v1/', data=input)
    input = {
        "token": user0['token'],
        "u_id": user0['u_id']
    }
    assert requests.get(config.url + '/user/profile/v1/', params=input).json()["user"]["email"] == "0001@unsw.edu.au"

import pytest
import requests
from src import config
from src.error import AccessError, InputError

# assumption: when token and handle are valid, but the handle
# entered by the user is same with previous handle, InputError will be raised

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
    return {
        "token": user0['token'],
        "u_id": user0['auth_user_id']
    }


# test invalid token with valid handle, this should raise AccessError
def test_invalid_token_and_valid_handle(clear_and_register_user0):
    user0 = clear_and_register_user0
    input = {
        "token": user0['token'] + "1",
        "handle_str": "abcd"
    }
    assert requests.put(config.url + 'user/profile/sethandle/v1', json=input).status_code == AccessError.code


# test invalid token with invalid handle, this should raise AccessError
def test_invalid_token_and_invalid_handle(clear_and_register_user0):
    user0 = clear_and_register_user0
    input = {
        "token": user0['token'] + "1",
        "handle_str": "a"
    }
    assert requests.put(config.url + 'user/profile/sethandle/v1', json=input).status_code == AccessError.code

# test valid token with invalid handle, this should raise InputError
# handle is invalid when len(handle) < 3 or len(handle) > 20 or is not alphanumeric
def test_valid_token_and_invalid_handle(clear_and_register_user0):
    user0 = clear_and_register_user0
    input = {
        "token": user0['token'],
        "handle_str": "a"
    }
    assert requests.put(config.url + 'user/profile/sethandle/v1', json=input).status_code == InputError.code
    input['handle_str'] = "a" * 50
    assert requests.put(config.url + 'user/profile/sethandle/v1', json=input).status_code == InputError.code
    input['handle_str'] = "!@#$%^" 
    assert requests.put(config.url + 'user/profile/sethandle/v1', json=input).status_code == InputError.code

# test valid token and handle, but the handle is used by others, this should raise InputError
def test_handle_used_by_others(clear_and_register_user0):
    user0 = clear_and_register_user0
    user1_register = {
        "email" : "0001@unsw.edu.au",
        "password" : "password",
        "name_first" : "firstname1",
        "name_last" : "lastname1",
    }
    user1 = requests.post(config.url + 'auth/register/v2', json=user1_register).json()
    input = {
        "token": user0['token'],
        "handle_str": "firstname1lastname1"
    }
    assert requests.put(config.url + 'user/profile/sethandle/v1', json=input).status_code == InputError.code
    input['token'] = user1['token']
    input['handle_str'] = "firstname0lastname0"
    assert requests.put(config.url + 'user/profile/sethandle/v1', json=input).status_code == InputError.code
    

# test valid token and handle, but the same as previous, this should raise InputError
def test_same_handle_as_previous(clear_and_register_user0):
    user0 = clear_and_register_user0
    input = {
        "token": user0['token'],
        "handle_str": "firstname0lastname0"
    }
    assert requests.put(config.url + 'user/profile/sethandle/v1', json=input).status_code == InputError.code

# test valid token with valid handle
def test_valid_token_and_valid_handle(clear_and_register_user0):
    user0 = clear_and_register_user0
    input = {
        "token": user0['token'],
        "handle_str": "firstname0lastname1"
    }
    requests.put(config.url + 'user/profile/sethandle/v1', json=input)

    input = {
        "token": user0['token'],
        "u_id": user0['u_id']
    }
    assert requests.get(config.url + 'user/profile/v1', params=input).json()["user"]["handle_str"] == "firstname0lastname1"

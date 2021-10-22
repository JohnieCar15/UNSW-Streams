import pytest
import requests
from src import config
from src.error import AccessError, InputError

# assumption: when token and name are valid, but the firstname/lastname
# entered by the user is same with previous name, InputError will be raised


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
    user2 = requests.post(config.url + 'auth/register/v2', json=user2_register).json()
    return {
        "token": user0['token'],
        "u_id": user0['auth_user_id']
    }


# test invalid token with valid name, this should raise AccessError
def test_invalid_token_and_valid_name(clear_and_register_user0):
    user0 = clear_and_register_user0
    input = {
        "token": user0['token'] + "1",
        "name_first": "firstname0",
        "name_last": "lastname0"
    }
    assert requests.put(config.url + 'user/profile/setname/v1', json=input).status_code == AccessError.code


# test invalid token with invalid name, this should raise AccessError
def test_invalid_token_and_invalid_name(clear_and_register_user0):
    user0 = clear_and_register_user0
    input = {
        "token": user0['token'] + "1",
        "name_first": "",
        "name_last": "lastname0"
    }
    assert requests.put(config.url + 'user/profile/setname/v1', json=input).status_code == AccessError.code


# test valid token with invalid name, this should raise InputError
def test_valid_token_and_invalid_name(clear_and_register_user0):
    user0 = clear_and_register_user0
    input = {
        "token": user0['token'],
    }
    first = ["", "a" * 51, "name"]
    last = ["", "a" * 51, "name"]
    for first_name in first:
        input["name_first"] = first_name
        for last_name in last:
            if first_name == last_name and first_name == "name":
                continue
            input["name_last"] = last_name
            assert requests.put(config.url + 'user/profile/setname/v1', json=input).status_code == InputError.code


# test valid token with valid name but first and last name all same with previous name, 
# this should raise InputError by assumption
def test_same_name_as_previous(clear_and_register_user0):
    user0 = clear_and_register_user0
    input = {
        "token": user0['token'] ,
        "name_first": "firstname0",
        "name_last": "lastname0"
    }
    assert requests.put(config.url + 'user/profile/setname/v1', json=input).status_code == InputError.code


# test valid token with valid name but same with others, this should still work because same name is allowed
def test_same_name_with_others(clear_and_register_user0):
    user0 = clear_and_register_user0
    user1_register = {
        "email" : "0001@unsw.edu.au",
        "password" : "password",
        "name_first" : "firstname1",
        "name_last" : "lastname1",
    }

    user1 = requests.post(config.url + 'auth/register/v2', json=user1_register).json()
    input = {
        "token": user1['token'],
        "name_first": "firstname0",
        "name_last": "lastname0"
    }
    requests.put(config.url + 'user/profile/setname/v1', json=input)
    input = {
        "token": user0['token'],
        "u_id": user1['auth_user_id']
    }
    profile_user1 = requests.get(config.url + 'user/profile/v1', params=input).json()
    assert profile_user1["user"]["name_first"] == "firstname0"
    assert profile_user1["user"]["name_last"] == "lastname0"


# test valid token with valid name
def test_valid_token_and_valid_name(clear_and_register_user0):
    user0 = clear_and_register_user0
    input = {
        "token": user0['token'],
        "name_first": "first",
        "name_last": "last"
    }
    requests.put(config.url + 'user/profile/setname/v1', json=input)
    input = {
        "token": user0['token'],
        "u_id": user0['u_id']
    }
    profile_user0 = requests.get(config.url + 'user/profile/v1', params=input).json()
    assert profile_user0["user"]["name_first"] == "first"
    assert profile_user0["user"]["name_last"] == "last"

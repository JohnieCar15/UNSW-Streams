import pytest
import requests
from src import config
from src.error import AccessError


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
        "token_valid": user0['token'],
        "u_id": user0['auth_user_id']
    }

# test invalid token and this should raise AccessError
def test_invalid_token(clear_and_register_user0):
    user0 = clear_and_register_user0
    input_token = {"token": user0['token_valid'] + "1"}
    assert requests.get(config.url + '/user/users/all/v1/', params=input_token).status_code == AccessError.code


def test_vaild_token_with_one_user_registered(clear_and_register_user0):
    user0 = clear_and_register_user0
    input_token = {"token": user0['token_valid']}
    assert requests.get(config.url + '/user/users/all/v1/', params=input_token).json() == {
        'users':[
            {'u_id': user0['auth_user_id'], 
            'email': "0000@unsw.edu.au", 
            "name_first": "firstname0", 
            "name_last": "lastname0",
            "handle_str": "firstname0lastname0"}
        ]
    } 


def test_vaild_token_with_many_user_registered():
    requests.delete(config.url + '/clear/v2')
    users_register = [
        {   "email" : "0000@unsw.edu.au",
            "password" : "password",
            "name_first" : "firstname0",
            "name_last" : "lastname0",
        }, {"email" : "0001@unsw.edu.au",
            "password" : "password",
            "name_first" : "firstname1",
            "name_last" : "lastname1",
        }, {"email" : "0002@unsw.edu.au",
            "password" : "password",
            "name_first" : "firstname2",
            "name_last" : "lastname2",
        }
    ]
    
    user0 = requests.post(config.url + '/auth/register/v2', data=users_register[0]).json()
    user1 = requests.post(config.url + '/auth/register/v2', data=users_register[1]).json()
    user2 = requests.post(config.url + '/auth/register/v2', data=users_register[2]).json()
    
    input_token = {"token": user0['token']}
    assert requests.get(config.url + '/user/users/all/v1/', params=input_token).json() == {
        'users': [
            {'u_id': user0['auth_user_id'],
            'email': "0000@unsw.edu.au",
            "name_first": "firstname0",
            "name_last": "lastname0",
            "handle_str": "firstname0lastname0"},

            {'u_id': user1['auth_user_id'], 
            'email': "0001@unsw.edu.au", 
            "name_first": "firstname1", 
            "name_last": "lastname1",
            "handle_str": "firstname1lastname1"},

            {'u_id': user2['auth_user_id'], 
            'email': "0002@unsw.edu.au", 
            "name_first": "firstname0", 
            "name_last": "lastname0",
            "handle_str": "firstname0lastname00"}
    ]}
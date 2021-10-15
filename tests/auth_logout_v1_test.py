import pytest
import requests

from src import config
from src.auth import auth_login_v1
from src.auth import auth_register_v1
from src.other import clear_v1
from src.error import AccessError

def test_auth_logout_v1():
    requests.delete(config.url + '/clear/v1')

    auth_register_input = {
        'email':'valid@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last':'Last'
    }

    token = requests.post(config.url + 'auth/register/v2', json=auth_register_input).json()['token']

    requests.post(config.url + 'auth/logout/v1', params={'token': token})

    # assert token is not valid

def test_invalid_token():
    requests.delete(config.url + '/clear/v1')

    auth_register_input = {
        'email':'valid@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last':'Last'
    }

    token = requests.post(config.url + 'auth/register/v2', json=auth_register_input).json()['token']

    requests.delete(config.url + '/clear/v1')

    logout_return = requests.post(config.url + 'auth/logout/v1', params={'token': token})

    assert register_return.status_code == AccessError.code 

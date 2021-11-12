import pytest
import requests

from src import config
from src.error import AccessError

def test_auth_passwordreset_request_v1():
    requests.delete(config.url + '/clear/v1')

    auth_register_input = {
        'email':'t13abeagle@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last':'Last'
    }

    token = requests.post(config.url + 'auth/register/v2', json=auth_register_input).json()['token']

    request_return = requests.post(config.url + 'auth/passwordreset/request/v1', json={'email': 't13abeagle@gmail.com'})

    logout_return = requests.post(config.url + 'auth/logout/v1', json={'token': token})

    assert logout_return.status_code == AccessError.code

    assert request_return.status_code == 200

def test_invalid_email():
    requests.delete(config.url + '/clear/v1')

    request_return = requests.post(config.url + 'auth/passwordreset/request/v1', json={'email': 'invalid@gmail.com'})

    assert request_return.status_code == 200

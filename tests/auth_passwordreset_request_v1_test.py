import pytest
import requests

from src import config
from src.error import AccessError

def test_auth_passwordreset_request_v1():
    requests.delete(config.url + '/clear/v1')

    auth_register_input = {
        'email':'valid@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last':'Last'
    }

    token = requests.post(config.url + 'auth/register/v2', json=auth_register_input).json()['token']

    requests.post(config.url + 'auth/passwordreset/request/v1', json={'email': 'valid@gmail.com'})

    logout_return = requests.post(config.url + 'auth/logout/v1', json={'token': token})

    assert logout_return.status_code == AccessError.code

def test_invalid_email():
    requests.delete(config.url + '/clear/v1')

    reset_return = requests.post(config.url + 'auth/passwordreset/request/v1', json={'email': 'invalid@gmail.com'})

    assert reset_return.status_code == 200

import pytest
import requests

from src import config
from src.error import AccessError

'''
auth_logout_v1_test.py: All functions related to testing the auth_logout_v1 function
'''

def test_auth_logout_v1():
    '''
    Successful case of logging out a standard user
    '''
    requests.delete(config.url + 'clear/v1')

    auth_register_input = {
        'email':'valid@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last':'Last'
    }

    token = requests.post(config.url + 'auth/register/v2', json=auth_register_input).json()['token']

    another_auth_register_input = {
        'email':'another@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last':'Last'
    }

    requests.post(config.url + 'auth/register/v2', json=another_auth_register_input).json()['token']

    logout_return = requests.post(config.url + 'auth/logout/v1', json={'token': token})

    assert logout_return.status_code == 200

    logout_return = requests.post(config.url + 'auth/logout/v1', json={'token': token})

    assert logout_return.status_code == AccessError.code 

def test_invalid_token():
    '''
    Error case of logging out with invalid token
    '''
    requests.delete(config.url + 'clear/v1')

    logout_return = requests.post(config.url + 'auth/logout/v1', json={'token': None})

    assert logout_return.status_code == AccessError.code 

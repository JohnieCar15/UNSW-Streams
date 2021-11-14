import pytest
import requests

from src import config
from src.error import InputError, AccessError

'''
dm_leave_v1_test.py: All functions related to testing the dm_leave_v1 function 
'''

def test_dm_leave_v1():
    '''
    Successful case of leaving a dm
    '''
    requests.delete(config.url + '/clear/v1')

    auth_register_input = {
        'email':'valid@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last':'Last'
    }

    token_1 = requests.post(config.url + 'auth/register/v2', json=auth_register_input).json()['token']

    auth_register_input = {
        'email':'second@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last':'Last'
    }

    user_2 = requests.post(config.url + 'auth/register/v2', json=auth_register_input).json()
    token_2 = user_2['token']
    u_id_2 = user_2['auth_user_id']

    dm_id = requests.post(config.url + 'dm/create/v1', json={'token': token_1, 'u_ids': [u_id_2]}).json()['dm_id']

    requests.post(config.url + 'dm/leave/v1', json={'token': token_2, 'dm_id': dm_id})

    details_return_1 = requests.get(config.url + 'dm/details/v1', params={'token': token_1, 'dm_id': dm_id})
    details_return_2 = requests.get(config.url + 'dm/details/v1', params={'token': token_2, 'dm_id': dm_id})

    assert details_return_1.status_code != AccessError.code 
    assert details_return_2.status_code == AccessError.code

def test_invalid_dm_id():
    '''
    Error case of passing in an invalid dm_id
    '''
    requests.delete(config.url + '/clear/v1')

    auth_register_input = {
        'email':'valid@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last':'Last'
    }

    token = requests.post(config.url + 'auth/register/v2', json=auth_register_input).json()['token']

    requests.post(config.url + 'dm/create/v1', json={'token': token, 'u_ids': []}).json()['dm_id']

    leave_return = requests.post(config.url + 'dm/leave/v1', json={'token': token, 'dm_id': ''})

    assert leave_return.status_code == InputError.code

def test_non_member():
    '''
    Error case of leaving when not a member
    '''
    requests.delete(config.url + '/clear/v1')

    auth_register_input = {
        'email':'valid@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last':'Last'
    }

    token_1 = requests.post(config.url + 'auth/register/v2', json=auth_register_input).json()['token']

    auth_register_input = {
        'email':'second@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last':'Last'
    }

    token_2 = requests.post(config.url + 'auth/register/v2', json=auth_register_input).json()['token']

    dm_id = requests.post(config.url + 'dm/create/v1', json={'token': token_1, 'u_ids': []}).json()['dm_id']

    leave_return = requests.post(config.url + 'dm/leave/v1', json={'token': token_2, 'dm_id': dm_id})

    assert leave_return.status_code == AccessError.code

def test_invalid_token():
    '''
    Error case of passing an invalid token
    '''
    requests.delete(config.url + '/clear/v1')

    auth_register_input = {
        'email':'valid@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last':'Last'
    }

    token_1 = requests.post(config.url + 'auth/register/v2', json=auth_register_input).json()['token']

    auth_register_input = {
        'email':'second@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last':'Last'
    }

    u_id_2 = requests.post(config.url + 'auth/register/v2', json=auth_register_input).json()['auth_user_id']

    dm_id = requests.post(config.url + 'dm/create/v1', json={'token': token_1, 'u_ids': [u_id_2]}).json()['dm_id']

    leave_return = requests.post(config.url + 'dm/leave/v1', json={'token': '', 'dm_id': dm_id})

    assert leave_return.status_code == AccessError.code

def test_invalid_token_invalid_dm_id():
    '''
    Error case of passing an invalid token and dm_id
    '''
    requests.delete(config.url + '/clear/v1')

    leave_return = requests.post(config.url + 'dm/leave/v1', json={'token': '', 'dm_id': ''})

    assert leave_return.status_code == AccessError.code

import pytest
import requests

from src import config
from src.error import InputError, AccessError

'''
dm_remove_v1_test.py: All functions related to testing the dm_remove_v1 function 
'''

def test_dm_remove_v1():
    '''
    Successful case of removing a dm
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

    requests.post(config.url + 'dm/create/v1', json={'token': token_1, 'u_ids': [u_id_2]})
    dm_id = requests.post(config.url + 'dm/create/v1', json={'token': token_1, 'u_ids': [u_id_2]}).json()['dm_id']

    message_senddm_input = {
        'token': token_1,
        'dm_id': dm_id,
        'message': "message"
    }
    requests.post(config.url + 'message/senddm/v1', json=message_senddm_input)

    requests.delete(config.url + 'dm/remove/v1', json={'token': token_1, 'dm_id': dm_id})

    details_return = requests.get(config.url + 'dm/details/v1', params={'token': token_1, 'dm_id': dm_id})

    assert details_return.status_code == InputError.code

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

    remove_return = requests.delete(config.url + 'dm/remove/v1', json={'token': token, 'dm_id': ''})

    assert remove_return.status_code == InputError.code

def test_unauthorised_user():
    '''
    Error case of unauthorised user trying to delete dm
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

    remove_return = requests.delete(config.url + 'dm/remove/v1', json={'token': token_2, 'dm_id': dm_id})

    assert remove_return.status_code == AccessError.code

def test_invalid_token_valid_dm_id():
    '''
    Error case of passing invalid token with valid dm_id
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

    remove_return = requests.delete(config.url + 'dm/remove/v1', json={'token': '', 'dm_id': dm_id})

    assert remove_return.status_code == AccessError.code

def test_invalid_token_invalid_dm_id():
    '''
    Error case of passing invalid token and invalid dm_id
    '''
    requests.delete(config.url + '/clear/v1')

    remove_return = requests.delete(config.url + 'dm/remove/v1', json={'token': '', 'dm_id': ''})

    assert remove_return.status_code == AccessError.code

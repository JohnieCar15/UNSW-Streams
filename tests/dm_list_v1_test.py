import pytest
import requests

from src import config
from src.error import AccessError

def test_dm_list_v1():
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

    dm_list = requests.get(config.url + 'dm/list/v1', params={'token': token_1}).json()['dms']

    assert dm_list[0]['dm_id'] == dm_id

def test_invalid_token():
    requests.delete(config.url + '/clear/v1')

    list_return = requests.get(config.url + 'dm/list/v1', params={'token': ''})

    assert list_return.status_code == AccessError.code

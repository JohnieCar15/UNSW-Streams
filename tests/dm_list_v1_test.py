import pytest
import requests

from src import config
from src.error import AccessError

@pytest.fixture
def clear_register_create_dm():
    requests.delete(config.url + '/clear/v1')

    auth_register_input = {
        'email':'valid@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last':'Last'
    }

    token = requests.post(config.url + 'auth/register/v2', json=auth_register_input).json()['token']

    dm_id = requests.post(config.url + 'dm/create/v1', json={'token': token, 'u_ids': []}).json()['dm_id']

    return {
        'token': token,
        'dm_id': dm_id
    }


def test_dm_list_v1(clear_register_create_dm):
    token = clear_register_create_dm['token']

    dm_list = requests.get(config.url + 'dm/list/v1', params={'token': token}).json()['dms']

    assert dm_list[0]['dm_id'] == clear_register_create_dm['dm_id']

def test_invalid_token():
    requests.delete(config.url + '/clear/v1')

    list_return = requests.get(config.url + 'dm/list/v1', params={'token': ''})

    assert list_return.status_code == AccessError.code

def test_empty_dm_list(clear_register_create_dm):
    auth_register_input = {
        'email':'second@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last':'Last'
    }

    token_2 = requests.post(config.url + 'auth/register/v2', json=auth_register_input).json()['token']

    dm_list = requests.get(config.url + 'dm/list/v1', params={'token': token_2}).json()['dms']

    assert dm_list == [] 

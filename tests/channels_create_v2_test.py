import pytest
import requests
import json
from src import config
from src.error import InputError, AccessError
'''
channels_create_v2_test.py: All functions related to testing the channels_create_v2 function 
'''
@pytest.fixture
def clear_and_register():
    '''
    clears then registers a user
    '''
    requests.delete(config.url + 'clear/v1')
    register = requests.post(config.url + 'auth/register/v2', json={
        'email': 'yes@yes.com',
        'password': 'aaaaaa',
        'name_first': "firstname",
        "name_last": "lastname"
    })
    register_data = register.json()
    return register_data['token']

def test_valid_id_valid_name_public(clear_and_register):
    '''
    Testing the case of a valid id and valid name for a public channel 
    '''
    token = clear_and_register
    channels_create = requests.post(config.url + 'channels/create/v2', json={
        'token': token,
        'name': 'name',
        'is_public': True
    })
    channels_create_data = channels_create.json()
    channels_create_id = channels_create_data['channel_id']
    
    channels_list = requests.get(config.url + 'channels/list/v2', params={'token': token}).json()
    channels_list_id = channels_list['channels'][0]['channel_id']
    
    assert channels_create_id == channels_list_id

def test_valid_id_invalid_channel_name(clear_and_register):
    '''
    Testing the case of an invalid short channel name for a public channel 
    '''
    token = clear_and_register
    channels_create = requests.post(config.url + 'channels/create/v2', json={
        'token': token, 
        'name':"" , 
        'is_public': True
    })

    assert channels_create.status_code == InputError.code

def test_valid_id_invalid_channel_name_2(clear_and_register):
    '''
    Testing the case of an invalid long channel name for a public channel 
    '''
    token = clear_and_register
    channels_create = requests.post(config.url + 'channels/create/v2', json={
        'token': token, 
        'name': 'aaaaaaaaaaaaaaaaaaaaa', 
        'is_public': True
    })

    assert channels_create.status_code == InputError.code

def test_invalid_token_invalid_channel_name():
    '''
    Testing an invalid token passed in with an invalid short channel name for a public channel 
    '''
    channels_create = requests.post(config.url + 'channels/create/v2', json={
        'token': 1, 
        'name': "" , 
        'is_public': True
    })

    assert channels_create.status_code == AccessError.code

def test_invalid_token_invalid_channel_name_2():
    '''
    Testing an invalid token passed in with an invalid long channel name for a public channel 
    '''
    channels_create = requests.post(config.url + 'channels/create/v2', json={
        'token': 1, 
        'name': 'aaaaaaaaaaaaaaaaaaaaa', 
        'is_public': True
    })

    assert channels_create.status_code == AccessError.code

def test_invalid_id_valid_name_public():
    '''
    Testing an invalid id passed in with a valid channel name for a public channel 
    '''
    channels_create = requests.post(config.url + 'channels/create/v2', json={
        'token': 1, 
        'name': 'name', 
        'is_public': True
    })

    assert channels_create.status_code == AccessError.code

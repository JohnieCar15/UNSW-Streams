import pytest
import requests
from src import config
from src.error import InputError

'''
clear_v1_test.py: All tests relating to clear_v1 function
'''

def test_register_login():
    '''
    Tests logging in after clearing data store
    '''
    requests.delete(config.url + '/clear/v1')
    auth_register_input = {
        'email' : "valid@gmail.com",
        'password' : "password",
        'name_first' : "First",
        'name_last' : "Last",
    }

    # Register new user
    requests.post(config.url + '/auth/register/v2', json=auth_register_input).json()

    requests.delete(config.url + '/clear/v1')

    auth_login_input = {
        'email' : "valid@gmail.com",
        'password' : "password",
    }

    # Attempt to login with user that was registered before clear
    assert requests.post(config.url + '/auth/login/v2', json=auth_login_input).status_code == InputError.code

def test_register_twice():
    '''
    Tests if registering again after clearing works
    '''
    requests.delete(config.url + '/clear/v1')

    auth_register_input = {
        'email' : "valid@gmail.com",
        'password' : "password",
        'name_first' : "First",
        'name_last' : "Last",
    }

    # Register user
    requests.post(config.url + '/auth/register/v2', json=auth_register_input).json()

    requests.delete(config.url + '/clear/v1')

    auth_register_input = {
        'email' : "valid@gmail.com",
        'password' : "password",
        'name_first' : "First",
        'name_last' : "Last",
    }

    # Assert that no error is raised 
    assert requests.post(config.url + '/auth/register/v2', json=auth_register_input).json()

def test_channel_details():
    '''
    Tests checking channel details after clearing data store
    '''
    requests.delete(config.url + '/clear/v1')

    auth_register_input1 = {
        'email' : "valid@gmail.com",
        'password' : "password",
        'name_first' : "First",
        'name_last' : "Last",
    }

    # Register new user
    token1 = requests.post(config.url + '/auth/register/v2', json=auth_register_input1).json()['token']

    channel_create_input = {
        'token' : token1,
        'name' : "channel",
        'is_public' : True
    }

    # Create new channel
    channel_id = requests.post(config.url + '/channels/create/v2', json=channel_create_input).json()['channel_id']

    requests.delete(config.url + '/clear/v1')

    auth_register_input2 = {
        'email' : "valid@gmail.com",
        'password' : "password",
        'name_first' : "First",
        'name_last' : "Last",
    }

    token2 = requests.post(config.url + '/auth/register/v2', json=auth_register_input2).json()['token']

    channel_details_input = {
        'token' : token2,
        'channel_id' : channel_id
    }

    # Attempt to get details of channel after clear
    assert requests.get(config.url + '/channel/details/v2', params = channel_details_input).status_code == InputError.code

def test_channel_join():
    '''
    Tests checking channel joining after clearing data store
    '''
    requests.delete(config.url + '/clear/v1')

    auth_register_input1 = {
        'email' : "valid@gmail.com",
        'password' : "password",
        'name_first' : "First",
        'name_last' : "Last",
    }

    token1 = requests.post(config.url + '/auth/register/v2', json=auth_register_input1).json()['token']

    channel_create_input = {
        'token' : token1,
        'name' : "channel",
        'is_public' : True
    }

    # Create new channel
    channel_id = requests.post(config.url + '/channels/create/v2', json=channel_create_input).json()['channel_id']

    requests.delete(config.url + '/clear/v1')

    auth_register_input2 = {
        'email' : "valid@gmail.com",
        'password' : "password",
        'name_first' : "First",
        'name_last' : "Last",
    }

    token2 = requests.post(config.url + '/auth/register/v2', json=auth_register_input2).json()['token']

    channel_join_input = {
        'token' : token2,
        'channel_id' : channel_id
    }

    # Attempt to join channel after clear
    assert requests.post(config.url + '/channel/join/v2', json=channel_join_input).status_code == InputError.code

def test_channel_message():
    '''
    Tests checking channel messages after clearing data store
    '''
    requests.delete(config.url + '/clear/v1')

    auth_register_input1 = {
        'email' : "valid@gmail.com",
        'password' : "password",
        'name_first' : "First",
        'name_last' : "Last",
    }

    token1 = requests.post(config.url + '/auth/register/v2', json=auth_register_input1).json()['token']

    channel_create_input = {
        'token' : token1,
        'name' : "channel",
        'is_public' : True
    }

    # Create new channel
    channel_id = requests.post(config.url + '/channels/create/v2', json=channel_create_input).json()['channel_id']

    requests.delete(config.url + '/clear/v1')

    auth_register_input2 = {
        'email' : "valid@gmail.com",
        'password' : "password",
        'name_first' : "First",
        'name_last' : "Last",
    }

    token2 = requests.post(config.url + '/auth/register/v2', json=auth_register_input2).json()['token']

    channel_message_input = {
        'token' : token2,
        'channel_id' : channel_id,
        'start' : 0
    }

    # Attempt to access messages after store is cleared
    assert requests.get(config.url + '/channel/messages/v2', params = channel_message_input).status_code == InputError.code

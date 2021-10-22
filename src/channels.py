from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
from src.helpers import validate_token, filter_data_store


def channels_list_v2(token):
    '''
    channels_list_v2: provides a list of all channels (and their associated details) that the authorised user is part of.
    
    Arguments:
        auth_user_id  - integer    - auth_id of the user
    
    Exceptions:
        No InputError will be raised in this function  
        AccessError - Occurs when auth_user is invalid
    
    Return Value:
        Returns a dictionary contains list of channels that the user belongs to when auth_user is valid
        For example: { 'channels': [{'channel_id': 1, 'name': channel_1}, 
                                    {'channel_id': 2, 'name': channel_2}]}
    '''
    store = data_store.get()

    # Checking if token is valid
    # if token can not be decoded
    # raise AccessError("Invalid token")
    auth_user_id = validate_token(token)['user_id']
    
    # initilise the returned list
    list_of_channel = []

    # loop through all channels stored and check if the channel contains that user
    for channel in store['channels']:
        # if the channel contains that user, add related details to channel_details
        if auth_user_id in channel['members']:
            channel_details = {'channel_id': channel['id'], 'name': channel['name']}
            # append channel_details to list_of_channel
            list_of_channel.append(channel_details)
    # { 'channels': [] } will be returned if the user not belong to any channels
    return { 'channels': list_of_channel }


def channels_listall_v2(token):
    '''
    channels_listall_v2: Provide a list of all channels, including private channels,
    (and their associated details)

    Arguments:
        auth_user_id - integer    - auth_id of the user

    Exceptions:
        No InputError will be raised in this function  
        AccessError - Occurs when auth_user is invalid

    Return Value:
        Returns a dictionary contains all the channels in the stream when auth_user is valid
        For example: { 'channels': [{'channel_id': 1, 'name': channel_1}, 
                                    {'channel_id': 2, 'name': channel_2}]}
    '''
    store = data_store.get()

    # Checking if token is valid
    # if token can not be decoded
    # raise AccessError("Invalid token")
    validate_token(token)['user_id']
    
    # initilise the returned list
    list_of_channel = []
    # loop through all channels stored
    for channel in store['channels']:
        # append channel_details to list_of_channel
        list_of_channel.append({'channel_id': channel['id'], 'name': channel['name']})
    
    return { 'channels': list_of_channel }


def channels_create_v2(token, name, is_public):
    '''
    channels_create_v2: creates a new channel with the given name and is set to either public or private. Also user who created it is made the owner.

    Arguments:
        token (string) - token string used to authorise and authenticate the user 
        name (string) - name of the channel id to be made
        is_public (bool) - Sets the channel to public or private 

    Exceptions:
        InputError  - Length of name is less than 1 or more than 20 characters
        AccessError - Occurs when token is invalid

    Return Value:
        Returns {channel_id} on successful run 

'''
    store = data_store.get()

    # check if token is valid
    auth_user_id = validate_token(token)

    # check if name is valid
    if len(name) < 1 or len(name) > 20:
        raise InputError(description="Invalid name length")

    # channel id will be length of existing list + 1
    new_id = len(store['channels']) + 1

    # store a dictionary containing the following
    channel_dictionary = {
        'id': new_id,
        'name': name,
        'owner': [auth_user_id],
        'is_public': is_public,
        'members': [auth_user_id],
        'messages': []
    }
    store['channels'].append(channel_dictionary)
    data_store.set(store)
    return {
        'channel_id': new_id
    }
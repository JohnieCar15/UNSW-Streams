from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
from src.helpers import validate_token, filter_data_store


def channels_create_v2(token, name, is_public):
    '''
    channels_create_v2:
    Creates a new channel with the given name and is set to either public or private. Also user who created it is made the owner.

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
    auth_user_id = validate_token(token)['user_id']

    # check if name is valid
    if len(name) < 1 or len(name) > 20:
        raise InputError(description="Invalid name length")

    # channel id will be length of existing list + 1
    new_id = len(store['dms']) + len(store['removed_dms']) + len(store['channels']) + 1

    # store a dictionary containing the following
    channel_dictionary = {
        'id': new_id,
        'name': name,
        'owner': [auth_user_id],
        'is_public': is_public,
        'members': [auth_user_id],
        'messages': [],
        'standup_active': False,
        'standup_messages': []
    }
    store['channels'].append(channel_dictionary)
    data_store.set(store)
    return {
        'channel_id': new_id
    }


def channels_list_v2(token):
    '''
    channels_list_v2: provides a list of all channels (and their associated details) that the authorised user is part of.
    
    Arguments:
        token  - string    - token of the user
    
    Exceptions:
        No InputError will be raised in this function  
        AccessError - Occurs when token is invalid
    
    Return Value:
        Returns a dictionary contains list of channels that the user belongs to when auth_user is valid
        For example: { 'channels': [{'channel_id': 1, 'name': channel_1}, 
                                    {'channel_id': 2, 'name': channel_2}]}
    '''

    # Checking if token is valid
    # if token can not be decoded
    # raise AccessError(description="Invalid token")
    auth_user_id = validate_token(token)['user_id']
   
    list_of_channel = filter_data_store(store_list='channels', key='members', value=auth_user_id)
    list_of_channel = [{'channel_id': channel['id'], 'name': channel['name']} for channel in list_of_channel]

    # { 'channels': [] } will be returned if the user not belong to any channels
    return { 'channels': list_of_channel }


def channels_listall_v2(token):
    '''
    channels_listall_v2: Provide a list of all channels, including private channels,
    (and their associated details)

    Arguments:
        token - string    - token of the user

    Exceptions:
        No InputError will be raised in this function  
        AccessError - Occurs when token is invalid

    Return Value:
        Returns a dictionary contains all the channels in the stream when auth_user is valid
        For example: { 'channels': [{'channel_id': 1, 'name': channel_1}, 
                                    {'channel_id': 2, 'name': channel_2}]}
    '''
    store = data_store.get()

    # Checking if token is valid
    # if token can not be decoded
    # raise AccessError(description="Invalid token")
    validate_token(token)['user_id']
    
    # initilise the returned list
    list_of_channel = []
    # loop through all channels stored
    for channel in store['channels']:
        # append channel_details to list_of_channel
        list_of_channel.append({'channel_id': channel['id'], 'name': channel['name']})
    
    return { 'channels': list_of_channel }


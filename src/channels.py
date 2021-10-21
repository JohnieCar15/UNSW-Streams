from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
from src.helpers import validate_token, filter_data_store

def channels_create_v2(token, name, is_public):
    '''
    channels_create_v2: creates a new channel with the given name and is set to either public or private. Also user who created it is made the owner.

    Arguments:
        token (int) - user_id of the user who called the function 
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
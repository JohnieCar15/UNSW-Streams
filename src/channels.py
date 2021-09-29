from src.data_store import data_store
from src.error import InputError
from src.error import AccessError

def channels_list_v1(auth_user_id):
    return {
        'channels': [
        	{
        		'channel_id': 1,
        		'name': 'My Channel',
        	}
        ],
    }

def channels_listall_v1(auth_user_id):
    store = data_store.get()
    # check if user_id valid
    if auth_user_id not in [user['id'] for user in store['users']]:
        raise AccessError("Invalid user_id")
    list_of_channel = []

    for channel in store['channels']:
        channel_details = {}
        channel_details['channel_id'] = channel['id']
        channel_details['name'] = channel['name']
        list_of_channel.append(channel_details)
        
    return { 'channels': list_of_channel }


def channels_create_v1(auth_user_id, name, is_public):
    
    store = data_store.get()

    # check if user_id valid 
    if auth_user_id not in [user['id'] for user in store['users']]:
        raise AccessError("Invalid user_id")

    # check if name is valid
    if (len(name) < 1 or len(name) > 20):
        raise InputError("Invalid name length")
    
    # channel id will be len of existing list + 1 
    new_id = len(store['channels']) + 1
    # store a dictionary containing the following 
    channel_dictionary = {'id': new_id, 'name': name, 'owner': auth_user_id, 'is_public': is_public, 'members': [auth_user_id]}
    store['channels'].append(channel_dictionary)
    
    return {
        'channel_id': new_id,
    }

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
    return {
        'channels': [
        	{
        		'channel_id': 1,
        		'name': 'My Channel',
        	}
        ],
    }

def channels_create_v1(auth_user_id, name, is_public):
    
    store = data_store.get()

    # check if user_id valid 
    if auth_user_id not in [user[0] for user in store['users']]:
        raise AccessError("Invalid user_id")

    # check if name is valid
    if (len(name) < 1 or len(name) > 20):
        raise InputError("Invalid name length")
    
    # channel id will be len of existing list + 1 
    new_id = len(store['channels']) + 1
    # store a tuple containing the following 
    store['channels'].append([new_id, name, auth_user_id, is_public,[auth_user_id]])
    
    return {
        'channel_id': new_id,
    }

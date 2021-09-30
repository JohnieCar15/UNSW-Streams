from src.data_store import data_store
from src.error import InputError, AccessError

def channel_invite_v1(auth_user_id, channel_id, u_id):
    store = data_store.get()
    user_id_list = [user['id'] for user in store['users']]
    if auth_user_id not in user_id_list:
        raise AccessError("Invalid auth_user_id")

    channel_list = [channel for channel in store['channels'] if channel['id'] == channel_id]
    if len(channel_list) == 0:
        raise InputError("Invalid channel_id")
    elif auth_user_id not in channel_list[0]['members']:
        raise AccessError('Auth user is not a member of channel')
    elif u_id not in user_id_list:
        raise InputError("Invalid u_id")
    elif u_id in channel_list[0]['members']:
        raise InputError('User already member of channel')
    else:
        channel_list[0]['members'].append(u_id)
    
    data_store.set(store)

    return {}

def channel_details_v1(auth_user_id, channel_id):
    return {
        'name': 'Hayden',
        'owner_members': [
            {
                'u_id': 1,
                'email': 'example@gmail.com',
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
                'handle_str': 'haydenjacobs',
            }
        ],
        'all_members': [
            {
                'u_id': 1,
                'email': 'example@gmail.com',
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
                'handle_str': 'haydenjacobs',
            }
        ],
    }

def channel_messages_v1(auth_user_id, channel_id, start):
    return {
        'messages': [
            {
                'message_id': 1,
                'u_id': 1,
                'message': 'Hello world',
                'time_created': 1582426789,
            }
        ],
        'start': 0,
        'end': 50,
    }

def channel_join_v1(auth_user_id, channel_id):
    store = data_store.get()
    user_id_list = [user['id'] for user in store['users']]
    if auth_user_id not in user_id_list:
        raise AccessError("Invalid user_id")

    channel_list = [channel for channel in store['channels'] if channel['id'] == channel_id]
    if len(channel_list) == 0:
        raise InputError("Invalid channel_id")
    elif auth_user_id in channel_list[0]['members']:
        raise InputError('User already member of channel')
    elif not channel_list[0]['is_public']:
        raise AccessError("User cannot join private channel")
    else:
        channel_list[0]['members'].append(auth_user_id)
    
    data_store.set(store)

    return {}

from src.data_store import data_store
from src.error import InputError, AccessError

def channel_invite_v1(auth_user_id, channel_id, u_id):
    return {
    }

def channel_details_v1(auth_user_id, channel_id):
    
    store = data_store.get()

    # check if auth_user_id is valid
    if auth_user_id not in [user['id'] for user in store['users']]:
        raise AccessError("Invalid user_id")
    
    # check if channel id is valid
    if channel_id not in [channel['id'] for channel in store['channels']]:
        raise AccessError("Invalid channel_id")

    # check if user is member of channel
    for channel in store['channels']:
        if channel_id == channel['id']:
            if auth_user_id not in channel['members']:
                raise AccessError("Not a member of channel")

    for channel in store['channels']:
        if channel_id == channel['id']:
            channel_name = channel['name']
            channel_is_public = channel['is_public']
            channel_members = channel['members']
            channel_owner_id = channel['owner']

    for user in store['users']:
        if channel_owner_id == user['id']:
            owner_email = user['email']
            owner_name_f = user['name_first']
            owner_name_l = user['name_last']
            # owner_handle = users['handle']

    all_members_list = []

    for member in store['users']:
        if member['id'] in channel_members:
            member_email = member['email']
            member_name_f = member['name_first']
            member_name_l = member['name_last']
            # member_handle = member['handle']
            member_dict = {'u_id': member['id'], 'email': member_email, 'name_first': member_name_f, 'name_last': member_name_l, 'handle_str': 'firstnamelastname'}
            all_members_list.append(member_dict)

    return {
        'name': channel_name,
        'is_public': channel_is_public,
        'owner_members': [
            {
                'u_id': channel_owner_id ,
                'email': owner_email ,
                'name_first': owner_name_f ,
                'name_last': owner_name_l ,
                'handle_str': 'firstnamelastname',
            }
        ],
        'all_members': all_members_list ,
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

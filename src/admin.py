from src.data_store import data_store
from src.error import AccessError, InputError
from src.helpers import validate_token, filter_data_store


# Helper Function
def is_global_owner(u_id):
    user_dict = filter_data_store(store='users', key='id',value=u_id)
    return user_dict['permission_id'] == 1

# Helper Function
def is_last_global_owner(u_id):
    global_owner_list = filter_data_store(store='users', key='permission_id', value=1)
    return len(global_owner_list) == 1 and global_owner_list[0]['id'] == u_id

# Helper Function
def remove_user_from_all_channels(channel_list, u_id):
    for channel_dict in channel_list:
        # Replacing contents of messages with 'Removed user'
        for message_dict in channel_dict['messages']:
            if message_dict['u_id'] == u_id:
                message_dict['message'] = 'Removed user'
        
        # Removing user from list of channel members
        channel_dict['members'].remove(u_id)
        # Removing user from list of channel owners if applicable
        if u_id in channel_dict['owner']:
            channel_dict['owner'].remove(u_id)


def admin_user_remove_v1(token, u_id):
    '''
    admin_user_remove_v1: Given a user by their u_id, remove them from the Streams.
    Arguments:
        token (str)         - Token string used to authorise and authenticate the user
        u_id (int)          - User id of the user that the admin wishes to remove

    Exceptions:
        InputError  - Occurs when u_id does not refer to a valid user
                    - Occurs when u_id refers to a user who is the only global owner
        AccessError - Occurs when the authorised user is not a global owner
                    - Occurs when the token passed in is not a valid token
                    
    Return Value:
        Returns {} on successful token and u_id
    '''
    store = data_store.get()
    # Checking that the token is valid and returning the decoded token
    auth_user_dict = validate_token(token)

    # Checking the auth user is global owner
    if not is_global_owner(auth_user_dict['user_id']):
        raise AccessError(description='The authorised user is not a global owner')

    # Checking the u_id entered is valid
    removed_user_dict = filter_data_store(store='users', key='id', value=u_id)
    if removed_user_dict is None:
        raise InputError(description='u_id does not refer to a valid user')

    # Checking if the u_id refers to the last global owner
    if is_last_global_owner(u_id):
        raise InputError(description='u_id refers the only global owner')

    # remove from dm and channel (could replace lines with channel/list and dm/list)
    #filtered_channel_list = [channel for channel in store['channel'] if u_id in channel['members']]
    #filtered_dm_list = [dm for dm in store['dm'] if u_id in dm['members']]
    filtered_channel_list = filter_data_store(store='channels', key='members', value=u_id)
    remove_user_from_all_channels(filtered_channel_list, u_id)

    filtered_dm_list = filter_data_store(store='dms', key='members', value=u_id)
    remove_user_from_all_channels(filtered_dm_list, u_id)


    # Removing users and setting relevant parameters
    removed_user_dict['is_removed'] = True
    removed_user_dict['name_first'] = 'Removed'
    removed_user_dict['name_last'] = 'user'
    removed_user_dict['email'] = ''
    removed_user_dict['handle_str'] = ''


    
    data_store.set(store)
    return {}

    

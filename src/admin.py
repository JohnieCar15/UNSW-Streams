from src.data_store import data_store
from src.error import AccessError, InputError
from src.helpers import validate_token, filter_data_store, is_global_owner

'''
admin.py: This file contains all functions relating to admin endpoints.

Admin Functions:
    - admin_userpermission_change_v1(token, u_id, permission_id)
    - admin_user_remove_v1(token, u_id)

Admin Helper functions:
    - check_valid_permission_id(permission_id)
    - is_last_global_owner(u_id)
    - remove_user_from_all_channels(channel_list, u_id)
'''

def admin_userpermission_change_v1(token, u_id, permission_id):
    '''
    admin_userpermission_change_v1: 
    Given a user by their user ID, set their permissions to new permissions described by permission_id.

    Arguments:
        token (str)         - Token string used to authorise and authenticate the user
        u_id (int)          - User id of the user that the admin wishes to change
        permission_id (int) - Permission id that the admin wishes to change the user to

    Exceptions:
        InputError  - Occurs when u_id does not refer to a valid user
                    - Occurs when u_id refers to a user who is the only global owner
                      and they are being demoted to a user
                    - Occurs when permission_id is invalid
        AccessError - Occurs when the authorised user is not a global owner
                    - Occurs when the token passed in is not a valid token
                    
    Return Value:
        Returns {} on successful token and u_id
    '''
    store = data_store.get()
    # Checking that the token is valid and returning the decoded token
    auth_user_dict = validate_token(token)

    # Checking the auth user is a global owner
    if not is_global_owner(auth_user_dict['user_id']):
        raise AccessError(description='The authorised user is not a global owner')

    # Checking the u_id entered is valid
    changed_user_dict = filter_data_store(store_list='users', key='id', value=u_id)
    if changed_user_dict == []:
        raise InputError(description='u_id does not refer to a valid user')

    # Checking if the u_id refers to the last global owner and they are demoted
    check_valid_permission_id(permission_id)
    if is_last_global_owner(u_id) and permission_id == 2:
        raise InputError(description='u_id refers the only global owner and they are being demoted to a user')

    changed_user_dict[0]['permission_id'] = permission_id
    data_store.set(store)
    return {}



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
    removed_user_dict = filter_data_store(store_list='users', key='id', value=u_id)
    if removed_user_dict == []:
        raise InputError(description='u_id does not refer to a valid user')

    # Checking if the u_id refers to the last global owner
    if is_last_global_owner(u_id):
        raise InputError(description='u_id refers the only global owner')

    # Remove user from all dms and channels and replacing messages sent
    filtered_channel_list = filter_data_store(store_list='channels', key='members', value=u_id)
    remove_user_from_all_channels(filtered_channel_list, u_id)

    filtered_dm_list = filter_data_store(store_list='dms', key='members', value=u_id)
    remove_user_from_all_channels(filtered_dm_list, u_id)


    store['users'].remove(removed_user_dict[0])

    # Removing users and setting relevant parameters
    removed_user_dict[0]['name_first'] = 'Removed'
    removed_user_dict[0]['name_last'] = 'user'
    removed_user_dict[0]['email'] = ''
    removed_user_dict[0]['handle_str'] = ''

    store['removed_users'].append(removed_user_dict[0])
 
    
    data_store.set(store)
    return {}



def check_valid_permission_id(permission_id):
    '''
    Checks that the permission id entered is valid (either 1 or 2)
    '''
    if permission_id not in (1, 2):
        raise InputError(description='permission_id is invalid')

def is_last_global_owner(u_id):
    '''
    Checks to see if the user id refers to the last global owner
    '''
    global_owner_list = filter_data_store(store_list='users', key='permission_id', value=1)
    return len(global_owner_list) == 1 and global_owner_list[0]['id'] == u_id

def remove_user_from_all_channels(channel_list, u_id):
    '''
    Removes the all traces of the user from all channels they are a member of
    '''
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
    

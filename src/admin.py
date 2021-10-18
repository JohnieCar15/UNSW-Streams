from src.data_store import data_store
from src.error import AccessError, InputError
from src.helpers import validate_token, filter_data_store


# Helper Function
def is_global_owner(u_id):
    user_dict = filter_data_store(list='users', key='id',value=u_id)
    return user_dict['permission_id'] == 1

# Helper Function
def is_last_global_owner(u_id):
    global_owner_list = filter_data_store(list='users', key='permission_id', value=1)
    return len(global_owner_list) == 1 and global_owner_list[0]['id'] == u_id


def admin_user_remove_v1(token, u_id):
    store = data_store.get()
    auth_user_dict = validate_token(token)

    if not is_global_owner(auth_user_dict['user_id']):
        raise AccessError(description='The authorised user is not a global owner')

    removed_user_dict = filter_data_store(list='users', key='id', value=u_id)
    if removed_user_dict is None:
        raise InputError(description='u_id does not refer to a valid user')

    if is_last_global_owner(u_id):
        raise InputError(description='u_id refers the only global owner')


    # remove from dm and channel (could replace lines with channel/list and dm/list)
    filtered_channel_list = [channel['id'] for channel in store['channel'] if u_id in channel['members']]
    filtered_dm_list = [dm['id'] for dm in store['dm'] if u_id in dm['members']]

    for channel_id in filtered_channel_list:
        channel_dict = filter_data_store(list='channels', key='id', value=channel_id)
        channel_dict['members'].remove(u_id)
        # Need to change this to deal with iteration 2 multiple owners
        if u_id in channel_dict['owner']:
            channel_dict['owner'].remove(u_id)

    for dm_id in filtered_dm_list:
        dm_dict = filter_data_store(list='dms', key='id', value=dm_id)
        dm_dict['members'].remove(u_id)
        # Not sure about this code and what happens to owners after profile is deleted
        '''if u_id in dm_dict['owner']:
            dm_dict['owner'].remove(u_id)'''

    # Removing users and setting relevant parameters
    removed_user_dict['is_removed'] = True
    removed_user_dict['name_first'] = 'Removed'
    removed_user_dict['name_last'] = 'user'
    removed_user_dict['email'] = ''
    removed_user_dict['handle_str'] = ''


    
    data_store.set(store)
    return {}



    

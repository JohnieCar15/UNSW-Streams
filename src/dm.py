from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import validate_token, filter_data_store

def dm_details_v1(token, dm_id):
    store = data_store.get()

    # check if token is valid
    auth_user_id = validate_token(token)

    # check if dm_id refers to valid dm
    if dm_id not in [dm['id'] for dm in store['dms']]:
        raise InputError(description='Invalid dm_id')
    
    # check if user is part of dm
    dm_dict = dm for dm in store['dms'] if dm_id == dm['id']
    if auth_user_id not in dm_dict['members']:
        raise AccessError(description="Not a member of DM")

    all_members_list = []

    # create dictionary for each member
    for member in store['users']:
        if member['id'] in dm_dict['members']:
            member_dict = {
                'u_id': member['id'],
                'email': member['email'],
                'name_first': member['name_first'],
                'name_last': member['name_last'],
                'handle_str': member['handle_str']
            }
            all_members_list.append(member_dict)


    return {
        'name': dm_dict['name']
        'members': all_members_list
    }
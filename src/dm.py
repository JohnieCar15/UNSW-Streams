from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import validate_token, filter_data_store

def dm_details_v1(token, dm_id):
    '''
    dm_details_v1: Given a valid authroised token and valid dm_id displays details for that dm 

    Arguments:
        token (string) - token string used to authorise and authenticate the user 
        dm_id    - id of the dm from which details are pulled 
        

    Exceptions:
        InputError  - Occurs when dm_id does not refer to a valid dm
        AccessError - Occurs when dm_id is valid but authorised user is not a member of the dm
        AccessError - Occurs when auth_user_id isn't valid 

    Return Value:
        Returns {name, members}
    '''

    store = data_store.get()

    # check if token is valid
    auth_user_id = validate_token(token)['user_id']

    # check if dm_id refers to valid dm
    dm_list = [dm['dm_id'] for dm in store['dms']]
    if len(dm_list) == 0:
        raise InputError(description='Invalid dm_id')
    
    # check if user is part of dm
    dm_dict = [dm for dm in store['dms'] if dm_id == dm['dm_id']][0]
    print (dm_dict)
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
        'name': dm_dict['name'],
        'members': all_members_list
    }

def dm_create_v1(token, u_ids):
    store = data_store.get()

    # check if token is valid
    auth_user_id = validate_token(token)['user_id']

    # check if any u_id in u_ids not valid
    for uid in u_ids:
        if uid not in filter_data_store(store_list='users', key='id'):
            raise InputError(description="Invalid user_id")
    
    # generate dm id
    new_id = len(store['dms']) + 1
    names = []
    u_ids.append(auth_user_id)
    u_ids = list(set(u_ids))
    for uid in u_ids:
        names.append(filter_data_store(store_list='users', key='id', value=uid)[0]['handle_str'])

    # automatically generating the DM name
    names.sort()
    name_str = ", ".join(names)

    dm_dictionary = {
        'dm_id': new_id,
        'name': name_str,
        'owner': [auth_user_id],
        'members': u_ids,
        'messages': []
    }
    store['dms'].append(dm_dictionary)
    data_store.set(store)
    return {
        'dm_id': new_id
    }

def dm_list_v1(token):
    store = data_store.get()

    auth_user_id = validate_token(token)['user_id']

    dms = []

    for dm in store['dms']:
        if auth_user_id in dm['members']:
            dm_dictionary = {
                'dm_id': dm['dm_id'],
                'name': dm['name']
            }
            dms.append(dm_dictionary)

    return {
        'dms': dms
    }
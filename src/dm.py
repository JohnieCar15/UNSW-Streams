from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import validate_token, filter_data_store

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
    print('U_IDS', u_ids)
    u_ids.append(auth_user_id)
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

def dm_leave_v1(token, dm_id):
    store = data_store.get()

    auth_user_id = validate_token(token)['user_id']

    found = False

    print('Store', store)

    for dm in store['dms']:
        if dm['dm_id'] == dm_id:
            found = True
            if auth_user_id not in dm['members']:
                raise AccessError(description='User is not a member of the DM')
            else:
                dm['members'].remove(auth_user_id)

    if not found:
        raise InputError(description='dm_id does not refere to valid DM')

    data_store.set(store)
    
    return {}
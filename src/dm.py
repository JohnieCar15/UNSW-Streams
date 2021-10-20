from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import validate_token, filter_data_store

def dm_create_v1(token, u_ids):
    store = data_store.get()

    # check if token is valid
    auth_user_id = validate_token(token)

    # check if any u_id in u_ids not valid
    for id in u_ids:
        if id not in [user['id'] for user in store['users']]:
            raise InputError(description="Invalid user_id")
    
    # generate dm id
    new_id = len(store['dms']) + 1
    names = []
    for id in u_ids:
        names.append(user['handle_str']) if user['id'] == id for user in store['users']:

    u_ids.append(auth_user_id)
    names.sort()
    name_str = ", ".join(names)
    
    dm_dictionary = {
        'dm_id': new_id
        'name': name_str
        'owner': auth_user_id
        'members': u_ids
        'messages': []
    }

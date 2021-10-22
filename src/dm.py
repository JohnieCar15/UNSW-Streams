from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import validate_token

def dm_leave_v1(token, dm_id):
    store = data_store.get()

    auth_user_id = validate_token(token)['user_id']

    found = False

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

def dm_remove_v1(token, dm_id):
    store = data_store.get()

    auth_user_id = validate_token(token)['user_id']

    found = False

    for dm in store['dms']:
        if dm['dm_id'] == dm_id:
            found = True
            if dm['owner'] != auth_user_id:
                raise AccessError(description='User is not the owner of the DM')
            else:
                dm['members'] = []

    if not found:
        raise InputError(description='dm_id does not refere to valid DM')

    data_store.set(store)
    
    return {}

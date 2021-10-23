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
    new_id = len(store['dms']) + len(store['channels']) + 1
    names = []
    u_ids.append(auth_user_id)
    for uid in u_ids:
        names.append(filter_data_store(store_list='users', key='id', value=uid)[0]['handle_str'])

    # automatically generating the DM name
    names.sort()
    name_str = ", ".join(names)

    dm_dictionary = {
        'id': new_id,
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
                'dm_id': dm['id'],
                'name': dm['name']
            }
            dms.append(dm_dictionary)

    return {
        'dms': dms
    }

def dm_messages_v1(token, dm_id, start):
    '''
    dm_messages_v1: Given a dm_id and start, returns up to 50 messages from start to start + 50,
    as well as the start and finishing indexes

    Arguments:
        token (string)    - token of a user
        dm_id (int)    - id of a dm
        start (int) - starting index of the messages to be returned
        ...

    Exceptions:
        InputError  - Occurs when invalid dm id is entered
                    - Occurs when start is greater than total number of messages
        AccessError - Occurs when user is not part of dm members

    Return Value:
        Returns {messages, 'start', 'end'} on successful token, dm_id and start

    '''
    store = data_store.get()

  # check if token is valid
    auth_user_id = validate_token(token)['user_id']

  # Checks if dm id is valid
    if dm_id not in filter_data_store(store_list='dms', key='id'):
        raise InputError(description="Invalid dm_id")
  # Finds the dm with the correct id
    new_dm = filter_data_store(store_list='dms', key='id', value=dm_id)[0]

  # Check if user is in dm members
    if auth_user_id not in new_dm['members']:
        raise AccessError(description="Invalid user_id")

    length = len(new_dm['messages']) - start
    # A negative length implies that start > length
    if length < 0:
        raise InputError(description="Start is greater than total number of messages")
    # Negative starts are invalid
    if start < 0:
      raise InputError(description="Invalid start")

    messages_dict = {}
    messages_dict['start'] = start
    # Deals with all cases
    if length == 0:
        messages_dict['end'] = -1
        messages_dict['messages'] = []
    elif length <= 50:
        messages_dict['end'] = -1
        # Create a copy of all messages from start up to final index
        messages_dict['messages'] = new_dm['messages'][start:start + length]
    else:
        messages_dict['end'] = start + 50
        messages_dict['messages'] = new_dm['messages'][start:start + 50]

    data_store.set(store)
        
    return messages_dict
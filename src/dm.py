from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import validate_token, filter_data_store

def dm_messages_v1(token, dm_id, start):
    store = data_store.get()

  # check if token is valid
    auth_user_id = validate_token(token)['user_id']

  # Checks if dm id is valid
    if dm_id not in [dm['id'] for dm in store['dms']]:
        raise InputError(description="Invalid dm_id")
  # Finds the dm with the correct id
    for dm in store['dms']:
        if dm['id'] == dm_id:
            new_dm = dm
            break
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
        messages_dict['messages'] = new_dm['messages'][start:start + length - 1]
    else:
        messages_dict['end'] = start + 50
        messages_dict['messages'] = new_dm['messages'][start:start + 49]

        
    return messages_dict

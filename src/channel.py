from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import validate_token, filter_data_store

'''
channel_messages_v2: Given a channel_id and start, returns up to 50 messages from start to start + 50,
as well as the start and finishing indexes

Arguments:
    auth_user_id (int)    - id of a user
    channel_id (int)    - id of a channel
    start (int) - starting index of the messages to be returned
    ...

Exceptions:
    InputError  - Occurs when invalid channel id is entered
                - Occurs when start is greater than total number of messages
    AccessError - Occurs when user is not part of channel members

Return Value:
    Returns {messages, 'start', 'end'} on successful auth_user_id, channel_id and start

'''
def channel_messages_v2(token, channel_id, start):
    store = data_store.get()

  # check if token is valid
    auth_user_id = validate_token(token)['user_id']

  # Checks if channel id is valid
    if channel_id not in filter_data_store(list='channels', key='id'):
        raise InputError(description="Invalid channel_id")
  # Finds the channel with the correct id
    new_channel = filter_data_store(list='channels', key='id', value=channel_id)[0]

  # Check if user is in channel members
    if auth_user_id not in new_channel['members']:
        raise AccessError(description="Invalid user_id")

    length = len(new_channel['messages']) - start
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
        messages_dict['messages'] = new_channel['messages'][start:start + length]
    else:
        messages_dict['end'] = start + 50
        messages_dict['messages'] = new_channel['messages'][start:start + 50]

    data_store.set(store)
        
    return messages_dict



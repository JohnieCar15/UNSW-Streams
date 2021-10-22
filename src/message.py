from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import validate_token, filter_data_store
from datetime import datetime, timezone

def message_edit_v1(token, message_id, message):
    '''
    message_edit_v1: Sends a message from an authorised user to a channel specified
    by a channel_id

    Arguments:
        token (string)    - token of a user
        message_id (int)    - id of a message
        message (string) - message to be sent
        ...

    Exceptions:
        InputError  - Occurs when invalid channel id is entered
                    - Length of message is more than 1000 characters
        AccessError - Occurs when user did not create message and is not owner

    Return Value:
        Returns {} on successful token, id and message

    '''
    store = data_store.get()

    # check if token is valid
    auth_user_id = validate_token(token)['user_id']

    # Checks if message exists
    # Contains extra field "channel_id"
    look_message = [message for message in store['messages'] if message['message']['message_id'] == message_id]

    if not look_message:
        raise InputError(description="Invalid message")
    else:
        messagedict = look_message[0]

    # Checks which channel the message is sent in and finds that message
    channel_dict = [channel for channel in store['channels'] if messagedict['channel_id'] == channel['id']][0]
    selected_message = [message for message in channel_dict['messages'] if message['message_id'] == message_id][0]

    # Checks if user is part of that channel
    if auth_user_id not in channel_dict['members']:
        raise AccessError(description="Not a member of channel")
    
    if auth_user_id != messagedict['message']['u_id'] and auth_user_id not in channel_dict['owner']:
        raise AccessError(description="Permission denied")

    if len(message) > 1000:
        raise InputError(description="Message is too long")

    if not message:
        store['messages'].remove(messagedict)
        channel_dict['messages'].remove(selected_message)
    else:
        messagedict['message']['message'] = message
        selected_message['message'] = message
        
    data_store.set(store)

    return {}

def message_send_v1(token, channel_id, message):
    '''
    message_send_v1: Sends a message from an authorised user to a channel specified
    by a channel_id

    Arguments:
        token (string)    - token of a user
        channel_id (int)    - id of a channel
        smessage (string) - message to be sent
        ...

    Exceptions:
        InputError  - Occurs when invalid channel id is entered
                    - Length of message is less than 1 character or more than 1000 characters
        AccessError - Occurs when user is not part of channel members

    Return Value:
        Returns {message_id} on successful token, id and message

    '''
    store = data_store.get()

    # check if token is valid
    auth_user_id = validate_token(token)['user_id']

    # Checks if channel id is valid
    if channel_id not in filter_data_store(store_list='channels', key='id', value=None):
        raise InputError(description="Invalid channel_id")

    # Filters data store for correct channel
    channel_dict = filter_data_store(store_list='channels', key='id', value=channel_id)[0]

    # Checks if user is part of channel members
    if auth_user_id not in channel_dict['members']:
        raise AccessError(description="Not a member of channel")

    # Checks if message is valid
    if len(message) < 1 or len(message) > 1000:
        raise InputError(description="Invalid message")

    # Sets up new keys for new message
    new_message = {}
    new_message['message_id'] = len(store['messages']) + 1
    new_message['u_id'] = auth_user_id
    new_message['message'] = message

    new_message['time_created'] = int(datetime.utcnow().timestamp())

    # Data store creates extra field of channel id for easier identification
    message_store = {}
    message_store['message'] = new_message
    message_store['channel_id'] = channel_id
    
    channel_dict['messages'].insert(0, new_message)
    store['messages'].insert(0, message_store)

    data_store.set(store)

    return { 
        'message_id': new_message['message_id']
    }



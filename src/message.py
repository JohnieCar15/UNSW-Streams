from src import auth, channel
from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import is_global_owner, validate_token, filter_data_store
from datetime import datetime

def message_edit_v1(token, message_id, message):
    '''
    message_edit_v1: Sends a message from an authorised user to a channel specified
    by a channel_id

    Arguments:
        token (string)    - token of a user
        message_id (int)    - id of a message
        message (string) - message to be sent
                         - Invalid token entered
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
    channel_dict = [channel for channel in (store['channels'] + store['dms']) if messagedict['channel_id'] == channel['id']][0]
    selected_message = [message for message in channel_dict['messages'] if message['message_id'] == message_id][0]

    # Checks if user is part of that channel
    if auth_user_id not in channel_dict['members']:
        raise AccessError(description="Not a member of channel")
    
    if auth_user_id != messagedict['message']['u_id'] and auth_user_id not in channel_dict['owner'] and not is_global_owner(auth_user_id):
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
        message (string) - message to be sent
        ...

    Exceptions:
        InputError  - Occurs when invalid channel id is entered
                    - Length of message is less than 1 character or more than 1000 characters
        AccessError - Occurs when user is not part of channel members
                    - Invalid token entered

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
    new_message = {
        'message_id': len(store['messages']) + len(store['removed_messages']) + 1,
        'u_id': auth_user_id,
        'message': message,
        'time_created': int(datetime.utcnow().timestamp()),
        'reacts' : [{
            'react_id' : 1,
            'u_ids' : [],
        }],
        'is_pinned' : False
    }

    # Data store creates extra field of channel id for easier identification
    message_store = {
        'message': new_message,
        'channel_id': channel_id
    }
    
    channel_dict['messages'].insert(0, new_message)
    store['messages'].insert(0, message_store)

    data_store.set(store)

    return { 
        'message_id': new_message['message_id']
    }

def message_senddm_v1(token, dm_id, message):
    '''
    message_senddm_v1: Sends a message from an authorised user to a channel specified
    by a channel_id

    Arguments:
        token (string)    - token of a user
        dm_id (int)       - id of a channel
        smessage (string) - message to be sent
        ...

    Exceptions:
        InputError  - Occurs when invalid dm id is entered
                    - Length of message is less than 1 character or more than 1000 characters
        AccessError - Occurs when user is not part of channel members
                    - Invalid token entered

    Return Value:
        Returns {message_id} on successful token, id and message

    '''
    store = data_store.get()

    # check if token is valid
    auth_user_id = validate_token(token)['user_id']

    # Checks if channel id is valid
    if dm_id not in filter_data_store(store_list='dms', key='id', value=None):
        raise InputError(description="Invalid channel_id")

    # Filters data store for correct channel
    dm_dict = filter_data_store(store_list='dms', key='id', value=dm_id)[0]

    # Checks if user is part of channel members
    if auth_user_id not in dm_dict['members']:
        raise AccessError(description="Not a member of channel")

    # Checks if message is valid
    if len(message) < 1 or len(message) > 1000:
        raise InputError(description="Invalid message")

    # Sets up new keys for new message
    new_message = {
        'message_id': len(store['messages']) + len(store['removed_messages']) + 1,
        'u_id': auth_user_id,
        'message': message,
        'time_created': int(datetime.utcnow().timestamp()),
        'reacts' : [{
            'react_id' : 1,
            'u_ids' : [],
        }],
        'is_pinned' : False
    }

    # Data store creates extra field of channel id for easier identification
    message_store = {
        'message': new_message,
        'channel_id': dm_id
    }
    
    dm_dict['messages'].insert(0, new_message)
    store['messages'].insert(0, message_store)

    data_store.set(store)

    return { 
        'message_id': new_message['message_id']
    }

def message_remove_v1(token, message_id):
    '''
    message_remove_v1: Deletes a message from an authorised user to a channel specified
    by a channel_id

    Arguments:
        token (string)    - token of a user
        dm_id (int)       - id of a channel
        ...

    Exceptions:
        InputError  - Occurs when invalid message id is entered
        AccessError - Invalid token entered
                    - Occurs when user did not make request and is not owner

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
    channel_dict = [channel for channel in (store['channels'] + store['dms']) if messagedict['channel_id'] == channel['id']][0]
    selected_message = [message for message in channel_dict['messages'] if message['message_id'] == message_id][0]

    # Checks if user is part of that channel
    if auth_user_id not in channel_dict['members']:
        raise AccessError(description="Not a member of channel")
    
    if auth_user_id != messagedict['message']['u_id'] and auth_user_id not in channel_dict['owner'] and not is_global_owner(auth_user_id):
        raise AccessError(description="Permission denied")
    
    # Remove selected messages from data store and channel messages
    store['removed_messages'].append(messagedict)
    store['messages'].remove(messagedict)
    channel_dict['messages'].remove(selected_message)

    data_store.set(store)

    return {}
    
def message_share_v1(token, og_message_id, message, channel_id, dm_id):
    '''
    message_share_v1: Shares a message to a DM or channel id, with an optional
    additional message.

    Arguments:
        token (string)       - token of a user
        og_message_id (int)  - id of original message
        message (string)     - additional message attached to shared message
        channel_id (int)     - id of channel being shared to. -1 if being shared to dm
        dm_id (int)          - id of dm being shared to. -1 if being shared to channel
        ...

    Exceptions:
        InputError  - Occurs when channel id or dm id are invalid
                    - Neither channel id or dm id are -1
                    - Both channel id and dm id are -1
                    - Message id does not refer to valid message
        AccessError - Invalid token entered
                    - Occurs when user is not part of channel/dm they are sending message to

    Return Value:
        Returns {shared_message_id} on successful token, og_message_id, message, channel_id and dm_id

    '''
    store = data_store.get()

    # check if token is valid
    auth_user_id = validate_token(token)['user_id']

    # Checks if either channel_id or dm_id is equal to -1
    if (channel_id == -1 and dm_id == -1) or (channel_id != -1 and dm_id != -1):
        raise InputError(description="only channel id or dm id can be equal to -1")
    
    if dm_id == -1:
        # Checks if channel id is valid
        if channel_id not in filter_data_store(store_list='channels', key='id', value=None):
            raise InputError(description="Invalid channel_id")
        final_id = channel_id
    else:
        # Checks if dm id is valid
        if dm_id not in filter_data_store(store_list='dms', key='id', value=None):
            raise InputError(description="Invalid dm_id")
        final_id = dm_id

    # Looks for the channel/dm this message is being sent to
    shared_channel_dict = [channel for channel in (store['channels'] + store['dms']) if final_id == channel['id']][0]

    # Check if the user is part of the channel/dm the message is being sent to 
    if auth_user_id not in shared_channel_dict['members']:
        raise AccessError(description="Not a member of channel")

    # Checks if message exists
    # Contains extra field "channel_id"
    look_message = [message for message in store['messages'] if message['message']['message_id'] == og_message_id]

    if not look_message:
        raise InputError(description="Invalid message")
    else:
        messagedict = look_message[0]

    # Checks which channel/dm the message is sent in and finds that message
    og_channel_dict = [channel for channel in (store['channels'] + store['dms']) if messagedict['channel_id'] == channel['id']][0]
    og_selected_message = [message for message in og_channel_dict['messages'] if message['message_id'] == og_message_id][0]

    # Checks if user is part of that channel
    if auth_user_id not in og_channel_dict['members']:
        raise InputError(description="Invalid message")

    if len(message) > 1000:
        raise InputError(description="Invalid message length")

    # Sets up new keys for new message
    new_message = {
        'message_id': len(store['messages']) + len(store['removed_messages']) + 1,
        'u_id': auth_user_id,
        'message': f"{message}" + "\n\n" + f'"""\n{og_selected_message["message"]}\n"""',
        'time_created': int(datetime.utcnow().timestamp())
    }

    # Data store creates extra field of channel id for easier identification
    message_store = {
        'message': new_message,
        'channel_id': final_id
    }

    shared_channel_dict['messages'].insert(0, new_message)
    store['messages'].insert(0, message_store)

    data_store.set(store)

    return {
        'shared_message_id' : new_message['message_id']
    }
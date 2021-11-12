from datetime import datetime, timezone
from threading import Timer
from src import auth, channel
from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import is_global_owner, validate_token, filter_data_store
from src.notifications import add_notification, find_tagged_users

'''
message.py: This file contains all functions relating to message endpoints.

Message Functions:
    - message_edit_v1(token, message_id, message)
    - message_send_v1(token, channel_id, message)
    - message_senddm_v1(token, dm_id, message)
    - message_remove_v1(token, message_id)
    - message_share_v1(token, og_message_id, message, channel_id, dm_id)
    - message_react_v1(token, message_id, react_id)
    - message_unreact_v1(token, message_id, react_id)
    - message_sendlaterdm_v1(token, dm_id, message, time_sent)
    - message_sendlater_v1(token, channel_id, message, time_sent)
    - message_pin_v1(token, message_id)
    - message_unpin_v1(token, message_id)

Message Helper Functions:
    - message_sendlater_v1_dummy(channel_id, new_message, channel_dict)
    - message_sendlaterdm_v1_dummy(dm_id, new_message, dm_dict)
'''

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
    # Contains extra fields "channel_id" and "is_dm"
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
        raise InputError(description="Invalid message id")
    
    # Firstly checks if user did not create message and is not the owner
    if auth_user_id != messagedict['message']['u_id'] and auth_user_id not in channel_dict['owner']:
        # Checks if message is sent in DM. If so, raise an AccessError
        if messagedict['is_dm'] == True:
            raise AccessError(description="Permission denied")
            # If sent in a channel, check if global owner
        else:
            # If user is also not global owner, raise AccessError
            if is_global_owner(auth_user_id) == False:
                raise AccessError(description="Permission denied")

    if len(message) > 1000:
        raise InputError(description="Message is too long")

    if not message:
        store['messages'].remove(messagedict)
        channel_dict['messages'].remove(selected_message)
    else:
        messagedict['message']['message'] = message
        selected_message['message'] = message

        # Checking if any users were tagged in the message and sending them a notification
        tagged_users_list = find_tagged_users(message)
        for u_id in tagged_users_list:
            if u_id in channel_dict['members']:
                add_notification(u_id, auth_user_id, channel_dict['id'], 'tagged', message)
        
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
    if channel_id not in filter_data_store(store_list='channels', key='id'):
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
        'message_id': len(store['messages']) + len(store['removed_messages']) + len(store['pending_messages']) + 1,
        'u_id': auth_user_id,
        'message': message,
        'time_created': int(datetime.now(timezone.utc).timestamp()),
        'reacts' : [{
            'react_id' : 1,
            'u_ids' : [],
        }],
        'is_pinned' : False
    }

    # Checking if any users were tagged in the message and sending them a notification
    tagged_users_list = find_tagged_users(message)
    for u_id in tagged_users_list:
        if u_id in channel_dict['members']:
            add_notification(u_id, auth_user_id, channel_id, 'tagged', message)

    # Data store creates extra field of channel id for easier identification
    message_store = {
        'message': new_message,
        'channel_id': channel_id,
        'is_dm' : False
    }
    
    channel_dict['messages'].insert(0, new_message)
    store['messages'].insert(0, message_store)

    data_store.set(store, user=auth_user_id, key='messages', key_value=1, user_value=1)

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
    if dm_id not in filter_data_store(store_list='dms', key='id'):
        raise InputError(description="Invalid dm_id")

    # Filters data store for correct channel
    dm_dict = filter_data_store(store_list='dms', key='id', value=dm_id)[0]

    # Checks if user is part of channel members
    if auth_user_id not in dm_dict['members']:
        raise AccessError(description="Not a member of dm")

    # Checks if message is valid
    if len(message) < 1 or len(message) > 1000:
        raise InputError(description="Invalid message")

    # Sets up new keys for new message
    new_message = {
        'message_id': len(store['messages']) + len(store['removed_messages']) + len(store['pending_messages']) + 1,
        'u_id': auth_user_id,
        'message': message,
        'time_created': int(datetime.now(timezone.utc).timestamp()),
        'reacts' : [{
            'react_id' : 1,
            'u_ids' : [],
        }],
        'is_pinned' : False
    }

    # Checking if any users were tagged in the message and sending them a notification
    tagged_users_list = find_tagged_users(message)
    for u_id in tagged_users_list:
        if u_id in dm_dict['members']:
            add_notification(u_id, auth_user_id, dm_id, 'tagged', message)

    # Data store creates extra field of channel id for easier identification
    message_store = {
        'message': new_message,
        'channel_id': dm_id,
        'is_dm' : True
    }
    
    dm_dict['messages'].insert(0, new_message)
    store['messages'].insert(0, message_store)

    data_store.set(store, user=auth_user_id, key='messages', key_value=1, user_value=1)

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
        raise InputError(description="Invalid message id")
    
    # Firstly checks if user did not create message and is not the owner
    if auth_user_id != messagedict['message']['u_id'] and auth_user_id not in channel_dict['owner']:
        # Checks if message is sent in DM. If so, raise an AccessError
        if messagedict['is_dm'] == True:
            raise AccessError(description="Permission denied")
            # If sent in a channel, check if global owner
        else:
            # If user is also not global owner, raise AccessError
            if is_global_owner(auth_user_id) == False:
                raise AccessError(description="Permission denied")
    
    # Remove selected messages from data store and channel messages
    store['removed_messages'].append(messagedict)
    store['messages'].remove(messagedict)
    channel_dict['messages'].remove(selected_message)

    data_store.set(store, user=auth_user_id, key='messages', key_value=-1, user_value=-1)

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
    
    check = True
    if dm_id == -1:
        # Checks if channel id is valid
        if channel_id not in filter_data_store(store_list='channels', key='id'):
            raise InputError(description="Invalid channel_id")
        check = False
        final_id = channel_id
    else:
        # Checks if dm id is valid
        if dm_id not in filter_data_store(store_list='dms', key='id'):
            raise InputError(description="Invalid dm_id")
        check = True
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
        'message_id': len(store['messages']) + len(store['removed_messages']) + len(store['pending_messages'])+ 1,
        'u_id': auth_user_id,
        'message': f"{message}" + "\n\n" + f'"""\n{og_selected_message["message"]}\n"""',
        'time_created': int(datetime.now(timezone.utc).timestamp()),
        'reacts' : [{
            'react_id' : 1,
            'u_ids' : [],
        }],
        'is_pinned' : False
    }

    # Data store creates extra field of channel id for easier identification
    message_store = {
        'message': new_message,
        'channel_id': final_id,
        'is_dm' : check
    }

    shared_channel_dict['messages'].insert(0, new_message)
    store['messages'].insert(0, message_store)

    # Checking if any users were tagged in the message and sending them a notification
    tagged_users_list = find_tagged_users(message)
    for u_id in tagged_users_list:
        if u_id in shared_channel_dict['members']:
            add_notification(u_id, auth_user_id, final_id, 'tagged', message)

    data_store.set(store, user=auth_user_id, key='messages', key_value=1, user_value=1)

    return {
        'shared_message_id' : new_message['message_id']
    }

def message_react_v1(token, message_id, react_id):
    '''
    message_react_v1: Given a message, add a 'react' to that particular message

    Arguments:
        token (string)    - token of a user
        message_id (int)  - id of message
        react_id (int)    - id of react
        ...

    Exceptions:
        InputError  - Occurs when invalid message id is entered
                    - Not valid react ID
                    - Message already contains react from user
        AccessError - Invalid token entered

    Return Value:
        Returns {} on successful token, message id and react id

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

    # Checks if user is part of that channel to access messages
    if auth_user_id not in channel_dict['members']:
        raise InputError(description="Invalid message ID")
    
    # Looks for particular message
    look_react = [react for react in selected_message['reacts'] if react['react_id'] == react_id]

    # If react ID does not exist, raise error
    if not look_react:
        raise InputError(description="Invalid react id")
    else:
        react_dict = look_react[0]

    # Raise error if user has already reacted to message
    if auth_user_id in react_dict['u_ids']:
        raise InputError(description="Already reacted to message")

    # Append user id to members that have reacted
    react_dict['u_ids'].append(auth_user_id)
    
    # Sending a notification to user invited to the channel/dm
    add_notification(selected_message['u_id'], auth_user_id, channel_dict['id'], 'react')

    data_store.set(store)

    return {}

def message_unreact_v1(token, message_id, react_id):
    '''
    message_unreact_v1: Given a message, removes a 'react' to that particular message

    Arguments:
        token (string)    - token of a user
        message_id (int)  - id of message
        react_id (int)    - id of react
        ...

    Exceptions:
        InputError  - Occurs when invalid message id is entered
                    - Not valid react ID
                    - Message already contains react from user
        AccessError - Invalid token entered

    Return Value:
        Returns {} on successful token, message id and react id

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

    # Checks if user is part of that channel to access message
    if auth_user_id not in channel_dict['members']:
        raise InputError(description="Invalid message ID")

    # Looks for particular message
    look_react = [react for react in selected_message['reacts'] if react['react_id'] == react_id]

    # If react ID does not exist, raise error
    if not look_react:
        raise InputError(description="Invalid react id")
    else:
        react_dict = look_react[0]

    # Raise error if user has not reacted to message
    if auth_user_id not in react_dict['u_ids']:
        raise InputError(description="No reaction to message")

    # Remove user from from users that have reacted
    react_dict['u_ids'].remove(auth_user_id)
    
    data_store.set(store)

    return {}

def message_sendlater_v1(token, channel_id, message, time_sent):
    '''
    message_sendlater_v1: Sends a message from a user to a channel in a specfied time
    in the future

    Arguments:
        token (string)             - token of a user
        channel_id (int)           - id of a channel
        message (string)           - message to be sent
        time_sent (UNIX timestamp) - time message is to be sent
        ...

    Exceptions:
        InputError  - Channel id is invalid
                    - Length of message is over 1000 characters
                    - Time_sent is in the past
        AccessError - Invalid token entered
                    - Occurs when user is not member of channel

    Return Value:
        Returns {message_id} on successful token, channel_id, message, time_sent

    '''
    store = data_store.get()

    # check if token is valid
    auth_user_id = validate_token(token)['user_id']

    # Checks if channel id is valid
    if channel_id not in filter_data_store(store_list='channels', key='id'):
        raise InputError(description="Invalid channel_id")

    # Filters data store for correct channel
    channel_dict = filter_data_store(store_list='channels', key='id', value=channel_id)[0]

    # Checks if user is part of channel members
    if auth_user_id not in channel_dict['members']:
        raise AccessError(description="Not a member of channel")

    # Checks if message is valid
    if len(message) < 1 or len(message) > 1000:
        raise InputError(description="Invalid message")

    # Calculate number of seconds into the future for timer to run
    seconds_difference = int(time_sent) - int(datetime.now(timezone.utc).timestamp())

    # Negative seconds implies time was sent in past 
    if seconds_difference < 0:  
        raise InputError(description="Invalid time")

    new_message = {
        'message_id': len(store['messages']) + len(store['removed_messages']) + len(store['pending_messages']) + 1,
        'u_id': auth_user_id,
        'message': message,
        'time_created': int(datetime.now(timezone.utc).timestamp()),
        'reacts' : [{
            'react_id' : 1,
            'u_ids' : [],
        }],
        'is_pinned' : False
    }

    # Stores request sent by user and time they made that request
    store['pending_messages'].insert(0, new_message)

    t = Timer(seconds_difference, message_sendlater_v1_dummy, [auth_user_id, channel_id, new_message, channel_dict])
    t.start()

    data_store.set(store)

    return {
        'message_id' : new_message['message_id']
    }

def message_sendlater_v1_dummy(auth_user_id, channel_id, new_message, channel_dict):
    '''
    Dummy function that runs after threading timer is finished 
    '''
    store = data_store.get()

    # Modifies new time to be when message is being sent
    new_message['time_created'] = int(datetime.now(timezone.utc).timestamp())

    # Data store creates extra field of channel id for easier identification
    message_store = {
        'message': new_message,
        'channel_id': channel_id,
        'is_dm' : False
    }
    
    channel_dict['messages'].insert(0, new_message)
    store['messages'].insert(0, message_store)

    # Removes message from pending messages store
    store['pending_messages'].remove(new_message)

    # Checking if any users were tagged in the message and sending them a notification
    tagged_users_list = find_tagged_users(new_message['message'])
    for u_id in tagged_users_list:
        if u_id in channel_dict['members']:
            add_notification(u_id, new_message['u_id'], channel_id, 'tagged', new_message['message'])

    data_store.set(store, user=auth_user_id, key='messages', key_value=1, user_value=1)

def message_sendlaterdm_v1(token, dm_id, message, time_sent):
    '''
    message_sendlaterdm_v1: Sends a message from a user to a DM in a specfied time
    in the future

    Arguments:
        token (string)             - token of a user
        dm_id (int)                - id of a DM
        message (string)           - message to be sent
        time_sent (UNIX timestamp) - time message is to be sent
        ...

    Exceptions:
        InputError  - DM id is invalid
                    - Length of message is over 1000 characters
                    - Time_sent is in the past
        AccessError - Invalid token entered
                    - Occurs when user is not member of DM

    Return Value:
        Returns {message_id} on successful token, dm_id, message, time_sent

    '''
    store = data_store.get()

    # check if token is valid
    auth_user_id = validate_token(token)['user_id']

    # Checks if dm id is valid
    if dm_id not in filter_data_store(store_list='dms', key='id'):
        raise InputError(description="Invalid dm_id")

    # Filters data store for correct dm
    dm_dict = filter_data_store(store_list='dms', key='id', value=dm_id)[0]

    # Checks if user is part of channel members
    if auth_user_id not in dm_dict['members']:
        raise AccessError(description="Not a member of dm")

    # Checks if message is valid
    if len(message) < 1 or len(message) > 1000:
        raise InputError(description="Invalid message")

    # Calculate number of seconds into the future for timer to run
    seconds_difference = int(time_sent) - int(datetime.now(timezone.utc).timestamp())

    # Negative seconds implies that time was sent in the past
    if seconds_difference < 0:
        raise InputError(description="Invalid time")

    new_message = {
        'message_id': len(store['messages']) + len(store['removed_messages']) + len(store['pending_messages']) + 1,
        'u_id': auth_user_id,
        'message': message,
        'time_created': int(datetime.now(timezone.utc).timestamp()),
        'reacts' : [{
            'react_id' : 1,
            'u_ids' : [],
        }],
        'is_pinned' : False
    }

    # Stores request sent by user and time they made that request
    store['pending_messages'].insert(0, new_message)

    t = Timer(seconds_difference, message_sendlaterdm_v1_dummy, [auth_user_id, dm_id, new_message, dm_dict])
    t.start()

    data_store.set(store)

    return {
        'message_id' : new_message['message_id']
    }

def message_sendlaterdm_v1_dummy(auth_user_id, dm_id, new_message, dm_dict):
    '''
    Dummy function that runs after threading timer is finished 
    '''
    store = data_store.get()

    # Modifies new time to be when message is being sent
    new_message['time_created'] = int(datetime.now(timezone.utc).timestamp())

    # Data store creates extra field of channel id for easier identification
    message_store = {
        'message': new_message,
        'channel_id': dm_id,
        'is_dm' : True
    }
    
    dm_dict['messages'].insert(0, new_message)
    store['messages'].insert(0, message_store)

    # Removes the message from the pending messages store
    store['pending_messages'].remove(new_message)

    # Checking if any users were tagged in the message and sending them a notification
    tagged_users_list = find_tagged_users(new_message['message'])
    for u_id in tagged_users_list:
        if u_id in dm_dict['members']:
            add_notification(u_id, new_message['u_id'], dm_id, 'tagged', new_message['message'])

    data_store.set(store, user=auth_user_id, key='messages', key_value=1, user_value=1)

def message_pin_v1(token, message_id):
    '''
    message_pin_v1: Given a message in a channel/DM, mark as "pinned"

    Arguments:
        token (string)    - token of a user
        message_id (int)  - id of a message
        ...

    Exceptions:
        InputError  - Occurs when message id is not valid message in channel/DM user has joined
                    - Message is already pinned
        AccessError - Message id is valid but user does not have owner permissions

    Return Value:
        Returns {} on successful token and message id

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
        raise InputError(description="Invalid message")

    # Firstly checks if user is an owner
    if auth_user_id not in channel_dict['owner']:
        # Checks if message is sent in DM. If so, raise an AccessError
        if messagedict['is_dm'] == True:
            raise AccessError(description="Permission denied")
            # If sent in a channel, check if global owner
        else:
            # If user is also not global owner, raise AccessError
            if is_global_owner(auth_user_id) == False:
                raise AccessError(description="Permission denied")

    if selected_message['is_pinned'] == True:
        raise InputError(description="Message is already pinned")

    selected_message['is_pinned'] = True

    data_store.set(store)

    return {}

def message_unpin_v1(token, message_id):
    '''
    message_unpin_v1: Given a message in a channel/DM, remove mark as "pinned"

    Arguments:
        token (string)    - token of a user
        message_id (int)  - id of a message
        ...

    Exceptions:
        InputError  - Occurs when message id is not valid message in channel/DM user has joined
                    - Message is not already pinned
        AccessError - Message id is valid but user does not have owner permissions

    Return Value:
        Returns {} on successful token and message id

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
        raise InputError(description="Invalid message")

    # Firstly checks if user is an owner
    if auth_user_id not in channel_dict['owner']:
        # Checks if message is sent in DM. If so, raise an AccessError
        if messagedict['is_dm'] == True:
            raise AccessError(description="Permission denied")
            # If sent in a channel, check if global owner
        else:
            # If user is also not global owner, raise AccessError
            if is_global_owner(auth_user_id) == False:
                raise AccessError(description="Permission denied")

    if selected_message['is_pinned'] == False:
        raise InputError(description="Message is not pinned")

    selected_message['is_pinned'] = False

    data_store.set(store)

    return {}

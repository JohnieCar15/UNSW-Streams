from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import validate_token, filter_data_store, is_global_owner
from datetime import datetime, timezone
import threading
import time

'''
standup.py: This file contains all functions relating to standup endpoints.

Standup Functions:
    - standup_start_v1(token, channel_id, length)
    - standup_active_v1(token, channel_id)
    - standup_send_v1(token, channel_id, message)

Standup Helper Functions:
    - standup_end(channel_dict, auth_user_id, time_finish)
'''

def standup_start_v1(token, channel_id, length):
    '''
    standup_start_v1:
    For a given channel start the standup period for the next "length" seconds. Returns time_finish

    Arguments:
        token (string) - token string used to authorise and authenticate the user 
        channel_id(int) - id of the channel for the standup to start
        length(int) - The time in seconds thats the meeting will go on for 

    Exceptions:      
        InputError - channel_id does not refer to a valid channel
        InputError  - length is a negative integer
        InputError - an active standup is currently running in the channel
      
      AccessError - channel_id is valid and the authorised user is not a member of the channel

    Return Value:
        Returns {time_finish} on successful run 

    '''
    store = data_store.get()

    # calculate time_finish
    time_finish = int(datetime.now(timezone.utc).timestamp() + (length))

    # check valid token 
    auth_user_id = validate_token(token)['user_id']

    # check valid channel id
    if channel_id not in filter_data_store(store_list='channels', key='id'):
        raise InputError(description="Invalid channel_id")

    # check is a member of channel 
    channel_dict = filter_data_store(store_list='channels', key='id', value=channel_id)[0]
    if auth_user_id not in channel_dict['members']:
        raise AccessError(description="Not a member of channel")

    # check if length is negative integer
    if length < 0:
        raise InputError(description="Length cannot be negative integer")

    # check if already an active standup
    if channel_dict['standup_active'] == True:
        raise InputError(description="Already an active standup")

    # set standup to be True 
    channel_dict['standup_active'] = True
    channel_dict['standup_finish'] = time_finish
    channel_dict['standup_messages'] = []

    # threading after length set standup to be False 
    t = threading.Timer(length, standup_end, [channel_dict, auth_user_id, time_finish])
    t.start()

    # Added for bonus feature
    # set user_status of the starter of standup 'busy'
    channel_dict['standup_attendee'].append(auth_user_id)
    starter_user = filter_data_store(store_list='users',key='id',value=auth_user_id)[0]
    starter_user['user_status'] = 'busy'
    starter_user['status_manually_set'] = False
    starter_user['standup_attending_now'].append(channel_id)


    data_store.set(store)
    return {'time_finish': time_finish}

def standup_end(channel_dict, auth_user_id, time_finish):
    '''
    Helper function used to end standup when time is up
    '''
    store = data_store.get()

    # send combined message
    standup_str = "\n".join(channel_dict['standup_messages'])
    standup_message = {
        'message_id': len(store['messages']) + len(store['removed_messages']) + len(store['pending_messages']) + 1,
        'u_id': auth_user_id,
        'message': standup_str,
        'time_created': time_finish,
        'reacts': [{
            'react_id': 1,
            'u_ids': [],
        }],
        'is_pinned': False
    }

    message_store = {
        'message': standup_message,
        'channel_id': channel_dict['id'],
        'is_dm': False
    }

    channel_dict['messages'].insert(0, standup_message)
    store['messages'].insert(0, message_store)

    # set standup_active to False
    channel_dict['standup_active'] = False
    channel_dict['standup_messages'] = []
    # set finish time to none
    channel_dict['standup_finish'] = None

    # Added for bonus feature
    # loop for all the attendee of the standup
    for user_id in channel_dict['standup_attendee']:
        #print(data_store.get())
        #print(channel_dict['standup_attendee'])
        #print(user_id)
        #print(filter_data_store(store_list='users',key='id',value=user_id))
        user = filter_data_store(store_list='users',key='id',value=user_id)[0]
        # remove the channel_id form user's standup_attending_now list
        if channel_dict['id'] in user['standup_attending_now']:
            user['standup_attending_now'].remove(channel_dict['id'])
        # if the user is not in any standup and not set status during any standups
        # set user_status to be 'available'
        if len(user['standup_attending_now']) == 0 and user['user_status'] == 'busy' and user['status_manually_set'] == False:
            user['user_status'] = 'available'
            user['status_manually_set'] = False
    # set standup_attendee to empty list
    channel_dict['standup_attendee'] = []
    
    data_store.set(store, user=auth_user_id, key='messages', key_value=1, user_value=1)

    return

def standup_active_v1(token, channel_id):
    '''
    standup_active_v1:
    For a given channel check if a startup is active. 

    Arguments:
        token (string) - token string used to authorise and authenticate the user 
        channel_id(int) - id of the channel for the standup to start
    Exceptions:      
        InputError - channel_id does not refer to a valid channel
        AccessError - channel_id is valid and the authorised user is not a member of the channel

    Return Value:
        Returns {is_active, time_finish} on successful run 

    '''
    # check valid token 
    auth_user_id = validate_token(token)['user_id']

    # check valid channel id
    if channel_id not in filter_data_store(store_list='channels',key='id'):
        raise InputError(description="Invalid channel_id")

    # check is a member of channel 
    channel_dict = filter_data_store(store_list='channels',key='id',value=channel_id)[0]
    if auth_user_id not in channel_dict['members']:
        raise AccessError(description="Not a member of channel")
    else: 
        return {'is_active': channel_dict['standup_active'], 'time_finish': channel_dict['standup_finish']}

def standup_send_v1(token, channel_id, message):
    '''
    standup_send_v1: Sending a message to get buffered in the standup queue 

    Arguments:
        token (string) - token string used to authorise and authenticate the user 
        channel_id(int) - id of the channel for the standup
        message (string) - message string to be sent to the standup
    Exceptions:      
        InputError - channel_id does not refer to a valid channel
        InputError - length of message is over 1000 characters
        InputError - an active standup is not currently running in the channel
        AccessError - channel_id is valid and the authorised user is not a member of the channel

    Return Value:
        Returns {} on successful run 

    '''
    store = data_store.get()

    # check valid token 
    auth_user_id = validate_token(token)['user_id']

    # check valid channel id
    if channel_id not in filter_data_store(store_list='channels',key='id'):
        raise InputError(description="Invalid channel_id")

    # check is a member of channel 
    channel_dict = filter_data_store(store_list='channels',key='id',value=channel_id)[0]
    if auth_user_id not in channel_dict['members']:
        raise AccessError(description="Not a member of channel")
        
    # check if length of message is over 1000 characters
    if len(message) > 1000:
        raise InputError(description="Message over 1000 characters")

    # check if standup is active
    if channel_dict['standup_active'] == False:
        raise InputError(description="No active standup")

    user_dict = filter_data_store(store_list='users', key='id', value=auth_user_id)[0]
    # add message to standup_messages
    standup_message = f"{user_dict['handle_str']}: {message}"
    channel_dict['standup_messages'].append(standup_message)
    # set user_status of the attendee of standup 'busy'
    channel_dict['standup_attendee'].append(auth_user_id)
    attendee = filter_data_store(store_list='users',key='id',value=auth_user_id)[0]
    attendee['user_status'] = 'busy'
    attendee['status_manually_set'] = False
    attendee['standup_attending_now'].append(channel_id)
    data_store.set(store)
    return {}

from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import validate_token, filter_data_store, is_global_owner
from datetime import datetime
import threading
import time

'''
standup.py: This file contains all functions relating to standup endpoints.

Standup Functions:
    - standup_start_v1(token, channel_id, length)
    - standup_end(channel_dict, auth_user_id, time_finish)
    - standup_active_v1(token, channel_id)
    - standup_send_v1(token, channel_id, message)
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
    # check valid token 
    auth_user_id = validate_token(token)['user_id']
    # check valid channel id
    if channel_id not in filter_data_store(store_list='channels',key='id'):
        raise InputError(description="Invalid channel_id")
    # check is a member of channel 
    channel_dict = filter_data_store(store_list='channels',key='id',value=channel_id)[0]
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
    # calculate time_finish
    time_finish = int(datetime.utcnow().timestamp() + (length))
    channel_dict['standup_finish'] = time_finish
    # threading after length set standup to be False 
    t = threading.Timer(length, standup_end, [channel_dict, auth_user_id, time_finish])
    t.start()
    data_store.set(store)
    # return time_finish
    return {'time_finish': time_finish}

def standup_end(channel_dict, auth_user_id, time_finish):
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
        'channel_id': channel_dict['id']
    }
    channel_dict['messages'].insert(0, standup_message)
    store['messages'].insert(0, message_store)
    # set standup_active to False
    channel_dict['standup_active'] = False
    # set finish time to none
    channel_dict['standup_finish'] = None
    data_store.set(store)

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
    # check if standup is active
    else: 
        return { 'is_active': channel_dict['standup_active'], 'time_finish': channel_dict['standup_finish']}

def standup_send_v1(token, channel_id, message):
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
    if channel_dict['standup_active'] == False:
        raise InputError(description="No active standup")
    user_dict = filter_data_store(store_list='users', key='id', value=auth_user_id)[0]
    # add message to standup_messages
    standup_message = f"{user_dict['handle_str']}: {message}"
    channel_dict['standup_messages'].append(standup_message)
    data_store.set(store)

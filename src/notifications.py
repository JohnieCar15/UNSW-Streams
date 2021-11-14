import re
from src.data_store import data_store
from src.helpers import validate_token, filter_data_store

'''
notifications.py: This file contains all functions relating to notifications endpoints.

Notifications Functions:
    - notifications_get_v1(token)

Notifications Helper Functions:
    - add_notification(u_id, trigger_u_id, channel_id, notification_type, message=None)
    - find_tagged_users(message)
'''

def notifications_get_v1(token):
    '''
    notifications_get_v1: Return the user's most recent 20 notifications, ordered from most recent to least recent.

    Arguments:
        token (str) - Token string used to authorise and authenticate the user

    Exceptions:
        AccessError - Occurs when the token passed in is not a valid token
                    
    Return Value:
        Returns { notifications } on successful token
    '''
    # Checking that the token is valid and returning the decoded token
    user_id = validate_token(token)['user_id']
    
    # Returning the user's 20 most recent notifications
    notifications_list = filter_data_store(store_list='users', key='id', value=user_id)[0]['notifications']
    return {'notifications': notifications_list[:20]}


def add_notification(u_id, trigger_u_id, channel_id, notification_type, message=None):
    '''
    Adds notification to the specified user's data store.
    '''
    store = data_store.get()
    notifications_list = filter_data_store(store_list='users', key='id', value=u_id)[0]['notifications']
    trigger_user_handle = filter_data_store(store_list='users', key='id', value=trigger_u_id)[0]['handle_str']

    channels_list = filter_data_store('channels', 'id', channel_id)
    dms_list = filter_data_store('dms', 'id', channel_id)
    channel_name = (channels_list + dms_list)[0]['name']

    notification = {
        'channel_id': channel_id if channels_list != [] else -1,
        'dm_id': channel_id if dms_list != [] else -1
    }

    if notification_type == 'tagged':
        notification['notification_message'] = f"{trigger_user_handle} tagged you in {channel_name}: {message[:20]}"
    if notification_type == 'react':
        notification['notification_message'] = f"{trigger_user_handle} reacted to your message in {channel_name}"
    if notification_type == 'invite':
        notification['notification_message'] = f"{trigger_user_handle} added you to {channel_name}"

    notifications_list.insert(0, notification)
    data_store.set(store)
    return

def find_tagged_users(message):
    '''
    Searching through the message and returning list of user ids of valid handles found
    '''
    store = data_store.get()
    tagged_list = re.findall('@([0-9a-zA-Z]+)', message)
    return [user['id'] for handle in tagged_list for user in store['users'] if handle in user['handle_str']]
        

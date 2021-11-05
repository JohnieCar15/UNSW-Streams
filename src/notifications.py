import re
from src.data_store import data_store
from src.error import AccessError, InputError
from src.helpers import validate_token, filter_data_store

def notifications_get_v1(token):
    # Checking that the token is valid and returning the decoded token
    user_id = validate_token(token)['user_id']
    
    # Returning the user's 20 most recent notifications
    notifications_list = filter_data_store(store_list='users', key='id', value=user_id)[0]['notifications']
    return {'notifications': notifications_list[:20]}


def add_notification(u_id, trigger_u_id, channel_id, notification_type, message=None):
    store = data_store.get()
    print('!!!!!!!!!!!!', notification_type)
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
    elif notification_type == 'react':
        notification['notification_message'] = f"{trigger_user_handle} reacted to your message in {channel_name}"
    elif notification_type == 'invite':
        print('!!!!!!!!!!!!')
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
    #NEED TO CHECK IF USER IS TAGGED MULTIPLE TIMES IN A SINGLE MESSAGE IF THEY ARE NOTIFIED EACH TIME
    return [user['id'] for handle in tagged_list for user in store['users'] if handle in user['handle_str']]
        

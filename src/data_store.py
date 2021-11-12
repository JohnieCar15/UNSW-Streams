from datetime import datetime, timezone
import pickle
'''
data_store.py

This contains a definition for a Datastore class which you should use to store your data.
You don't need to understand how it works at this point, just how to use it :)

The data_store variable is global, meaning that so long as you import it into any
python file in src, you can access its contents.

Example usage:

    from data_store import data_store

    store = data_store.get()
    print(store) # Prints { 'names': ['Nick', 'Emily', 'Hayden', 'Rob'] }

    names = store['names']

    names.remove('Rob')
    names.append('Jake')
    names.sort()

    print(store) # Prints { 'names': ['Emily', 'Hayden', 'Jake', 'Nick'] }
    data_store.set(store)
'''

## YOU SHOULD MODIFY THIS OBJECT BELOW
session_tracker = 0
SECRET = 'JOjQqnzcMKrLVsTVLNc2hzA4iWkqqcQB'

initial_object = {
    'users': [],
    'channels': [],
    'messages': [],
    'dms': [],
    'removed_users': [],
    'removed_messages': [],
    'removed_dms': [],
    'channels_exist': [],
    'dms_exist': [],
    'messages_exist': [],
    'users_in_channel_or_dm': [],
    'pending_messages' : []
}
'''
Data_store dictionary fields:
user = {
    'id': int,
    'email': str,
    'password': str,
    'name_first': str,
    'name_last': str,
    'handle_str': str,
    'permission_id': int,
    'session_list': [int session_id],
    'channels_joined': [{num_channels_joined, time_stamp}],
    'dms_joined':      [{num_dms_joined, time_stamp}],
    'messages_sent':   [{num_messages_sent, time_stamp}],
    'notifications': []
}

channel = {
    'id': int,
    'name': str,
    'owner': [int u_id],
    'is_public': bool,
    'members': [int u_id],
    'messages: []
}

dm = {
    'id': int,
    'name': str,
    'owner': [int u_id],
    'members': [int u_id],
    'messages: [message]
}

message = {
    'message_id': int,
    'u_id': int,
    'message': str,
    'time_created': int unix timestamp
}

message_store = {
    'message': message,
    'channel_id': int
    'is_dm' : bool
}

user_in_channel_or_dm = u_id (int)

notification = {
    'notification_message': str,
    'channel_id': int,
    'dm_id':int
}
'''
## YOU SHOULD MODIFY THIS OBJECT ABOVE
class Datastore:
    def __init__(self):
        try:
          self.__store = pickle.load(open("data_store.p", "rb"))
        except Exception:
          self.__store = initial_object

    def get(self):
        return self.__store

    def set(self, store, user=None, key=None, key_value=None, user_value=None):
        if not isinstance(store, dict):
            raise TypeError('store must be of type dictionary')
        store = update_store(store, user, key, key_value, user_value)
        self.__store = store
        with open('data_store.p', 'wb') as FILE:
            pickle.dump(store, FILE)

print('Loading Datastore...')

global data_store
data_store = Datastore()

def update_store(store, user=None, key=None, key_value=None, user_value=None):
    '''
    This helper fuction is used for user_stats and users_stats
    it will be callled with data_store.set(store, user, key, value, user_value), when there is a change
    of user's num_channels_joined/dms_joined/messages_sent or the total num of channels/dms/messages,
    and update the store

    Note that this fonction should not be put in helpers.py,
    bacause it will raise circular import as the other functions in it import data_store

    # channels_create will return (store, user, key='channel', key_value=1, user_value=1)
    # channel_invite will return  (store, use, key='channel', key_value=0, user_value=1)
    # channel_join will return    (store, user, key='channel', key_value=0, user_value=1)
    # channel_leave will return   (store, user, key='channel', key_value=0, user_value=-1)
    '''

    # key == None when the function called in server will not change num_channels/dms/messages
    if key == None:
        return store

    # get time_stamp and update channels/dms_exist/messages_sent
    time_stamp = int(datetime.now(timezone.utc).timestamp())
    update_channels_and_dms_and_messages_exist(store, key, key_value, time_stamp)

    # get new key for helper function: update_num_channels_dms_joined_or_message_sent()
    key_dict = {
        'channel': 'channels_joined',
        'dm': 'dms_joined',
        'messages': 'messages_sent'
    }
    new_key = key_dict[key]

    # some of fucntion will return user as a u_id, others will return a list of u_id
    # turn all of them to be list, and loop through
    user = [user] if type(user) != list else user
    for u_id in user:
        update_num_channels_dms_joined_or_message_sent(store, u_id, new_key, user_value, time_stamp)
        update_users_in_channel_or_dm(store=store, key=key, u_id=u_id, user_value=user_value)
    return store


def update_channels_and_dms_and_messages_exist(store, key, key_value, time_stamp):
    '''
    according to key and key_value, update num_channels/dms/messages_exist,
    key can be 'channel', 'dm', 'messages'
    key_value can be 1, 0, -1, 1 is adding one, 0 is unchanged, -1 is deleded one
    '''
    if key_value != 0:
        if key == 'channel':
            store['channels_exist'].append({'num_channels_exist': len(store['channels']), 'time_stamp': time_stamp})
        if key == 'dm':
            store['dms_exist'].append({'num_dms_exist': len(store['dms']), 'time_stamp': time_stamp})
        if key == 'messages':
            store['messages_exist'].append({'num_messages_exist': len(store['messages']), 'time_stamp': time_stamp})


def update_num_channels_dms_joined_or_message_sent(store, u_id, new_key, user_value, time_stamp):
    '''
    update channels_dms_joined and messages_sent of specific user
    '''
    # if message_remove is called, user_value == -1
    # but in this case the num_messages_sent by uesr will not change
    if new_key == 'messages_sent' and user_value < 0:
        return

    # get the user with specific u_id and update channels_dms_joined and messages_sent
    for user in store['users']:
        if user['id'] == u_id:
            append_value = user[new_key][-1]['num_' + new_key] + user_value
            user[new_key].append({'num_' + new_key: append_value, 'time_stamp': time_stamp})

def update_users_in_channel_or_dm(store, key, u_id, user_value):
    '''
    append or deleted the u_id to store['users_in_channel_or_dm']
    '''
    if key != 'channel' and key != 'dm':
        return
    # if the user create/join/be invited to a channel/dm,, and
    # the user is not in store['users_in_channel_or_dm']
    # then the u_id of that user will be appen to store['users_in_channel_or_dm']
    if user_value == 1 and u_id not in store['users_in_channel_or_dm']:
        store['users_in_channel_or_dm'].append(u_id)

    # if the user leave/be removed from a channel/dm,
    # and then that user is not in any channels and dms
    # the u_id of that user will be deleted from store['users_in_channel_or_dm']
    if user_value == -1:
        for user in store['users']:
            if user['id'] == u_id:
                if user['channels_joined'][-1]['num_channels_joined'] + user['dms_joined'][-1]['num_dms_joined'] == 0:
                    store['users_in_channel_or_dm'].remove(u_id)

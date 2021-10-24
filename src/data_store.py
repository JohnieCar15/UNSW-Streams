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
    'removed_dms': []
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
    'session_list': [int session_id]
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

    def set(self, store):
        if not isinstance(store, dict):
            raise TypeError('store must be of type dictionary')
        self.__store = store
        with open('data_store.p', 'wb') as FILE:
            pickle.dump(store, FILE)

print('Loading Datastore...')

global data_store
data_store = Datastore()

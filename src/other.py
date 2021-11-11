from src.data_store import data_store

'''
other.py: This file contains the other important functions used in the project

Functions:
    - clear_v1()
'''

def clear_v1():
    '''
    clear_v1: Resets internal data to initial state

    Return Value:
        Returns {} on successful run
    '''
    store = data_store.get()
    # Clear users and channels data store
    store['users'] = []
    store['channels'] = []
    store['messages'] = []
    store['dms'] = []
    store['removed_users'] = []
    store['removed_messages'] = []
    store['pending_messages'] = []
    store['removed_dms'] = []
    store['channels_exist'] = []
    store['dms_exist'] = []
    store['messages_exist'] = []
    store['users_in_channel_or_dm'] = []
    data_store.set(store)

    return {}

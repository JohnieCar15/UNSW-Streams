from src.data_store import data_store
'''
clear_v1: Resets internal data to initial state

Return Value:
    Returns {} on successful run
'''
def clear_v1():
    store = data_store.get()
    # Clear users and channels data store
    store['users'] = []
    store['channels'] = []
    store['messages'] = []
    store['dms'] = []
    store['removed_users'] = []
    store['removed_messages'] = []
    store['pending_messages'] = 0
    store['removed_dms'] = []
    data_store.set(store)

    return {}

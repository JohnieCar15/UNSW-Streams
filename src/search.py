from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import validate_token, filter_data_store, is_global_owner
'''
search.py: This file contains the search_v1 function.

Functions:
    - search_v1(token, query_str)
'''
def search_v1(token, query_str):
    '''
    search_v1:
    Given a query str return a collection of messaages that match the query str

    Arguments:
        token (string) - token string used to authorise and authenticate the user 
        query_str (string) - query string to search messages against 

    Exceptions:
        InputError - Occurs length of query_str is less than 1 or over 1000 characters
        AccessError - Occurs when token is invalid

    Return Value:
        Returns {messages} on successful run 
    '''
    store = data_store.get()
    # validate token
    auth_user_id = validate_token(token)['user_id']
    # check if str less than 1 or over 1000 characters
    if (len(query_str) < 1) or (len(query_str) > 1000):
        raise InputError(description="Query str cannot be less than 1 or over 1000 characters")
    
    # find all channels user is apart of
    channels_list = filter_data_store(store_list='channels', key='members', value=auth_user_id)
    # find all dms user is apart of
    dms_list = filter_data_store(store_list='dms', key='members', value=auth_user_id)

    messages_list = []
    for channel in channels_list:
        for message in channel['messages']:
            if query_str in message['message']:
                messages_list.append(message)
    
    for dm in dms_list:
        for message in dm['messages']:
            if query_str in message['message']:
                messages_list.append(message)

    for message in messages_list:
        for react in message['reacts']:
            react['is_this_user_reacted'] = True if auth_user_id in react['u_ids'] else False

    data_store.set(store)
    # return messages list
    return {'messages': messages_list}
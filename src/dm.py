from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import validate_token, filter_data_store
from src.notifications import add_notification

'''
dm.py: This file contains all functions relating to dm endpoints.

Dm Functions:
    - dm_create_v1(token, u_ids)
    - dm_list_v1(token)
    - dm_leave_v1(token, dm_id)
    - dm_details_v1(token, dm_id)
    - dm_messages_v1(token, dm_id, start)
    - dm_remove_v1(token, dm_id)
'''

def dm_create_v1(token, u_ids):
    '''
    dm_create_v1:
    Creates a new dm with the specified u_ids.

    Arguments:
        token (string) - token string used to authorise and authenticate the user 
        u_ids (list) - list of u_ids to be added to the dm

    Exceptions:
        InputError - Occurs when any u_id in u_ids does not refer to a valid user
        AccessError - Occurs when token is invalid

    Return Value:
        Returns {channel_id} on successful run 

    '''
    store = data_store.get()

    # check if token is valid
    auth_user_id = validate_token(token)['user_id']

    # check if any u_id in u_ids not valid
    for uid in u_ids:
        if uid not in filter_data_store(store_list='users', key='id'):
            raise InputError(description="Invalid user_id")
    
    # generate dm id
    new_id = len(store['dms']) + len(store['removed_dms']) + len(store['channels']) + 1
    names = []
    u_ids.append(auth_user_id)
    u_ids = list(set(u_ids))
    for uid in u_ids:
        names.append(filter_data_store(store_list='users', key='id', value=uid)[0]['handle_str'])

    # automatically generating the DM name
    names.sort()
    name_str = ", ".join(names)

    dm_dictionary = {
        'id': new_id,
        'name': name_str,
        'owner': [auth_user_id],
        'members': u_ids,
        'messages': []
    }
    store['dms'].append(dm_dictionary)
    data_store.set(store, user=u_ids, key='dm', key_value=1, user_value=1)

    for u_id in dm_dictionary['members']:
        if u_id != auth_user_id:
            # Sending a notification to users invited to the dm
            add_notification(u_id, auth_user_id, new_id, 'invite')

    return {
        'dm_id': new_id
    }

def dm_list_v1(token):
    '''
    dm_list_v1: provides a list of all channels (and their associated details) that the authorised user is part of.
    
    Arguments:
        token  - string    - token of the user
    
    Exceptions:
        No InputError will be raised in this function  
        AccessError - Occurs when token is invalid
    
    Return Value:
        Returns a dictionary contains list of channels that the user belongs to when auth_user is valid
        For example: { 'channels': [{'channel_id': 1, 'name': channel_1}, 
                                    {'channel_id': 2, 'name': channel_2}]}
    '''
    store = data_store.get()

    auth_user_id = validate_token(token)['user_id']

    dms = []

    for dm in store['dms']:
        if auth_user_id in dm['members']:
            dm_dictionary = {
                'dm_id': dm['id'],
                'name': dm['name']
            }
            dms.append(dm_dictionary)

    return {
        'dms': dms
    }

def dm_leave_v1(token, dm_id):
    '''
    dm_leave_v1: removes a given user from a given dm
    
    Arguments:
        token   - string    - token of the user
        dm_id   - int       - id of the dm
    
    Exceptions:
        InputError  - Occurs when dm_id does not exist 
        AccessError - Occurs when token is invalid
                    - Occurs when user is not a member of the dm
    
    Return Value:
        Returns {}
    '''
    store = data_store.get()

    auth_user_id = validate_token(token)['user_id']

    found = False

    for dm in store['dms']:
        if dm['id'] == dm_id:
            found = True
            if auth_user_id not in dm['members']:
                raise AccessError(description='User is not a member of the DM')
            
            dm['members'].remove(auth_user_id)

    if not found:
        raise InputError(description='dm_id does not refer to valid DM')

    data_store.set(store, user=auth_user_id, key='dm', key_value=0, user_value=-1)
    
    return {}

def dm_details_v1(token, dm_id):
    '''
    dm_details_v1: Given a valid authroised token and valid dm_id displays details for that dm 

    Arguments:
        token (string) - token string used to authorise and authenticate the user 
        dm_id    - id of the dm from which details are pulled 
        

    Exceptions:
        InputError  - Occurs when dm_id does not refer to a valid dm
        AccessError - Occurs when dm_id is valid but authorised user is not a member of the dm
        AccessError - Occurs when auth_user_id isn't valid 

    Return Value:
        Returns {name, members}
    '''

    store = data_store.get()

    # check if token is valid
    auth_user_id = validate_token(token)['user_id']

    # check if dm_id refers to valid dm
    if dm_id not in filter_data_store(store_list='dms',key='id'):
        raise InputError(description="Invalid dm_id")
    
    # check if user is part of dm
    dm_dict = filter_data_store(store_list='dms',key='id',value=dm_id)[0]
    if auth_user_id not in dm_dict['members']:
        raise AccessError(description="Not a member of DM")

    all_members_list = []
    # create dictionary for each member
    for member in store['users']:
        if member['id'] in dm_dict['members']:
            member_dict = {
                'u_id': member['id'],
                'email': member['email'],
                'name_first': member['name_first'],
                'name_last': member['name_last'],
                'handle_str': member['handle_str'],
                'profile_img_url': member['profile_img_url']
            }
            all_members_list.append(member_dict)


    return {
        'name': dm_dict['name'],
        'members': all_members_list
    }

def dm_messages_v1(token, dm_id, start):
    '''
    dm_messages_v1: Given a dm_id and start, returns up to 50 messages from start to start + 50,
    as well as the start and finishing indexes

    Arguments:
        token (string)    - token of a user
        dm_id (int)    - id of a dm
        start (int) - starting index of the messages to be returned
        ...

    Exceptions:
        InputError  - Occurs when invalid dm id is entered
                    - Occurs when start is greater than total number of messages
        AccessError - Occurs when user is not part of dm members

    Return Value:
        Returns {messages, 'start', 'end'} on successful token, dm_id and start

    '''
    store = data_store.get()

  # check if token is valid
    auth_user_id = validate_token(token)['user_id']

  # Checks if dm id is valid
    if dm_id not in filter_data_store(store_list='dms', key='id'):
        raise InputError(description="Invalid dm_id")
  # Finds the dm with the correct id
    new_dm = filter_data_store(store_list='dms', key='id', value=dm_id)[0]

  # Check if user is in dm members
    if auth_user_id not in new_dm['members']:
        raise AccessError(description="Invalid user_id")

    length = len(new_dm['messages']) - start
    # A negative length implies that start > length
    if length < 0:
        raise InputError(description="Start is greater than total number of messages")
    # Negative starts are invalid
    if start < 0:
      raise InputError(description="Invalid start")

    messages_dict = {}
    messages_dict['start'] = start
    # Deals with all cases
    if length == 0:
        messages_dict['end'] = -1
        messages_dict['messages'] = []
    elif length <= 50:
        messages_dict['end'] = -1
        # Create a copy of all messages from start up to final index
        messages_dict['messages'] = new_dm['messages'][start:start + length]
    else:
        messages_dict['end'] = start + 50
        messages_dict['messages'] = new_dm['messages'][start:start + 50]

    for message in messages_dict['messages']:
        for react in message['reacts']:
            react['is_this_user_reacted'] = True if auth_user_id in react['u_ids'] else False

    data_store.set(store)
        
    return messages_dict

def dm_remove_v1(token, dm_id):
    '''
    dm_remove_v1: removes a given dm
    
    Arguments:
        token   - string    - token of the user
        dm_id   - int       - id of the dm
    
    Exceptions:
        InputError  - Occurs when dm_id does not exist 
        AccessError - Occurs when token is invalid
                    - Occurs when user is not the owner of the dm
    
    Return Value:
        Returns {}
    '''
    store = data_store.get()

    auth_user_id = validate_token(token)['user_id']

    found = False
    u_ids = []

    for dm in store['dms']:
        if dm['id'] == dm_id:
            found = True
            if auth_user_id not in dm['owner']:
                raise AccessError(description='User is not the owner of the DM')
            
            for message in dm['messages']:
                message_store = {
                    'message': message,
                    'channel_id': dm_id,
                    'is_dm' : True
                }
                store['messages'].remove(message_store)
                store['removed_messages'].append(message_store)

            u_ids = dm['members']
            u_ids.extend(dm['owner'])
            u_ids = list(set(u_ids))
            dm['owner'] = []
            dm['members'] = []
            store['removed_dms'].append(dm)
            store['dms'].remove(dm)

    if not found:
        raise InputError(description='dm_id does not refer to valid DM')

    data_store.set(store, user=u_ids, key='dm', key_value=-1, user_value=-1)

    return {}

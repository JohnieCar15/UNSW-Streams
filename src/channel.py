from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import validate_token, filter_data_store, is_global_owner


def channel_join_v2(token, channel_id):
    '''
    channel_join_v2:
    Given a channel_id of a channel that the authorised user can join, adds them to that channel.

    Arguments:
        token (str)         - Token string used to authorise and authenticate the user
        channel_id (int)    - Channel id of the channel the user wishes to join

    Exceptions:
        InputError  - Occurs when channel_id does not refer to a valid channel
                    - Occurs when the authorised user is already a member of the channel
        AccessError - Occurs when channel_id refers to a channel that is private and the
                      authorised user is not already a channel member and is not a global owner
                    - Occurs when the token passed in is not a valid token
                    
    Return Value:
        Returns {} on successful auth_user_id and channel_id

    '''
    store = data_store.get()
    # Checking that the token is valid and returning the decoded token
    auth_user_id = validate_token(token)['user_id']

    channel_list = filter_data_store(store_list='channels', key='id', value=channel_id)

    # Checking if the channel_id is valid
    if channel_list == []:
        raise InputError(description="Invalid channel_id")
    # Checking if the auth_user_id is already member of the channel
    elif auth_user_id in channel_list[0]['members']:
        raise InputError(description='User already member of channel')
    # Checking if the channel is private and the auth user is not a global owner
    elif not is_global_owner(auth_user_id) and not channel_list[0]['is_public']:
        raise AccessError(description="User cannot join private channel")
    else:
        channel_list[0]['members'].append(auth_user_id)
    
    data_store.set(store)
    return {}

def channel_invite_v2(token, channel_id, u_id):
    '''
    channel_invite_v2: Invites a user with ID u_id to join a channel with ID channel_id.
    Arguments:
        token (str)         - Token string used to authorise and authenticate the user
        channel_id (int)    - Channel id of the channel the auth_user wishes to invite to
        u_id (int)          - User id of the user the auth_user wishes to invite

    Exceptions:
        InputError  - Occurs when channel_id does not refer to a valid channel
                    - Occurs when u_id does not refer to a valid user
                    - Occurs when u_id refers to a user who is already a member of the channel
        AccessError - Occurs when channel_id is valid and the authorised user is 
                      not a member of the channel
                    - Occurs when the token passed in is not a valid token
                    
    Return Value:
        Returns {} on successful token, channel_id and

    '''
    store = data_store.get()
    # Checking that the token is valid and returning the auth_user_id
    auth_user_id = validate_token(token)['user_id']

    channel_list = filter_data_store(store_list='channels', key='id', value=channel_id)

    # Checking if the channel_id is valid
    if channel_list == []:
        raise InputError(description="Invalid channel_id")
    # Checking if the auth_user_id is a member of the channel
    elif auth_user_id not in channel_list[0]['members']:
        raise AccessError(description='Auth user is not a member of channel')
    # Checking if the u_id is valid
    elif filter_data_store(store_list='users', key='id', value=u_id) == []:
        raise InputError(description="Invalid u_id")
    # Checking if the u_id is already a member of the channel
    elif u_id in channel_list[0]['members']:
        raise InputError(description='User already member of channel')
    
    channel_list[0]['members'].append(u_id)
    
    data_store.set(store)
    return {}

def channel_details_v2(token, channel_id):
    '''
    channel_details_v2: Given a valid authorised token and valid channel_id displays details for that channel 

    Arguments:
        token (string) - token string used to authorise and authenticate the user 
        channel_id    - id of the channel from which details are pulled 
        

    Exceptions:
        InputError  - Occurs when channel_id does not refer to a valid channel
        AccessError - Occurs when channel_id is valid but authorised user is not a member of the channel
        AccessError - Occurs when auth_user_id isn't valid 

    Return Value:
        Returns {name, is_public, owner_members, all_members}
    '''
    store = data_store.get()
    # check if token is valid
    auth_user_id = validate_token(token)['user_id']
    
    # check if channel_id refers to a valid id
    if channel_id not in filter_data_store(store_list='channels',key='id'):
        raise InputError(description="Invalid channel_id")
    
    # check if user is member of channel
    channel_dict = filter_data_store(store_list='channels',key='id',value=channel_id)[0]
    if auth_user_id not in channel_dict['members']:
        raise AccessError(description="Not a member of channel")

    # get variables for channel details from store['channels']
    channel_name = channel_dict['name']
    channel_is_public = channel_dict['is_public']
    channel_members = channel_dict['members']
    channel_owners = channel_dict['owner']
    all_owners_list = []
    # get variables for channel details - owner from store['users']
    for owner in store['users']:
        if owner['id'] in channel_owners:
            owner_dict = {
                'u_id': owner['id'],
                'email': owner['email'],
                'name_first': owner['name_first'],
                'name_last': owner['name_last'],
                'handle_str': owner['handle_str']
            }
            all_owners_list.append(owner_dict)

    # initialise members list of dictionaries
    all_members_list = []

    # create dictionary for each member
    for member in store['users']:
        if member['id'] in channel_members:
            member_dict = {
                'u_id': member['id'],
                'email': member['email'],
                'name_first': member['name_first'],
                'name_last': member['name_last'],
                'handle_str': member['handle_str']
            }
            all_members_list.append(member_dict)

    return {
        'name': channel_name,
        'is_public': channel_is_public,
        'owner_members': all_owners_list,
        'all_members': all_members_list
    }

def channel_messages_v2(token, channel_id, start):
    '''
    channel_messages_v2: Given a channel_id and start, returns up to 50 messages from start to start + 50,
    as well as the start and finishing indexes

    Arguments:
        token (string)    - token of a user
        channel_id (int)    - id of a channel
        start (int) - starting index of the messages to be returned
        ...

    Exceptions:
        InputError  - Occurs when invalid channel id is entered
                    - Occurs when start is greater than total number of messages
        AccessError - Occurs when user is not part of channel members

    Return Value:
        Returns {messages, 'start', 'end'} on successful token, channel_id and start

    '''
    store = data_store.get()

  # check if token is valid
    auth_user_id = validate_token(token)['user_id']

  # Checks if channel id is valid
    if channel_id not in filter_data_store(store_list='channels', key='id'):
        raise InputError(description="Invalid channel_id")
  # Finds the channel with the correct id
    new_channel = filter_data_store(store_list='channels', key='id', value=channel_id)[0]

  # Check if user is in channel members
    if auth_user_id not in new_channel['members']:
        raise AccessError(description="Invalid user_id")

    length = len(new_channel['messages']) - start
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
        messages_dict['messages'] = new_channel['messages'][start:start + length]
    else:
        messages_dict['end'] = start + 50
        messages_dict['messages'] = new_channel['messages'][start:start + 50]

    data_store.set(store)

    return messages_dict

def channel_leave_v1(token, channel_id):
    '''
    channel_leave_v1: Given a valid authorised token and valid channel_id displays removes token as a member of channel

    Arguments:
        token (string) - token string used to authorise and authenticate the user 
        channel_id    - id of the channel from which details are pulled 
        

    Exceptions:
        InputError  - Occurs when channel_id does not refer to a valid channel
        AccessError - Occurs when channel_id is valid but authorised user is not a member of the channel
        AccessError - Occurs when token isn't valid 

    Return Value:
        Returns {}

    '''
    store = data_store.get()

    # check if token is valid
    auth_user_id = validate_token(token)['user_id']

    # check if channel_id is valid
    if channel_id not in filter_data_store(store_list='channels',key='id'):
        raise InputError(description="Invalid channel_id")
    
    # check if auth_user_id member of channel
    channel_dict = filter_data_store(store_list='channels',key='id',value=channel_id)[0]
    if auth_user_id not in channel_dict['members']:
        raise AccessError(description="Not a member of channel")
    
    # remove auth_user_id from owner list if owner
    if auth_user_id in channel_dict['owner']:
        channel_dict['owner'].remove(auth_user_id)
   
    # remove auth_user_id from members list
    channel_dict['members'].remove(auth_user_id)
    
    data_store.set(store)
        
    return {}

def channel_removeowner_v1(token, channel_id, u_id):
    '''
    channel_removeowner_v1: 
    Given a valid authorised token, channel_id and u_id, it removes the user as an owner of channel

    Arguments:
        token (string) - token string used to authorise and authenticate the user 
        channel_id (int)   - id of the channel from which details are pulled 
        u_id  (int)  - id of the user to remove as owner 
        

    Exceptions:
        InputError  - Occurs when channel_id does not refer to a valid channel
        InputError  - Occurs when u_id does not refer to a valid user
        InputError  - Occurs when u_id does not refer to an owner of the channel
        InputError  - Occurs when u_id refers to a user who is currently the only owner of the channel
        AccessError - Occurs when channel_id is valid but authorised user is not a member of the channel
        AccessError - Occurs when token isn't valid 

    Return Value:
        Returns {}

    '''
    store = data_store.get()

    # check if token is valid
    auth_user_id = validate_token(token)['user_id']

    # check if channel id is valid
    if channel_id not in filter_data_store(store_list='channels',key='id'):
        raise InputError(description="Invalid channel_id")

    channel_dict = filter_data_store(store_list='channels',key='id',value=channel_id)[0]

    # check if user has owner permissions
    user_dict = filter_data_store(store_list='users',key='id',value=auth_user_id)[0]
    if auth_user_id not in channel_dict['owner'] and user_dict['permission_id'] != 1:
        raise AccessError(description='User does not have owner permissions in channel')
    
    # check if global owner they are a member of channel
    if auth_user_id not in channel_dict['members']:
        raise AccessError(description='User does not have owner permissions in channel')

    # check if u_id is valid
    if u_id not in filter_data_store(store_list='users', key='id'): 
        raise InputError(description="Invalid user_id")

    # check if user is an owner of the channel
    if u_id not in channel_dict['owner']:
        raise InputError(description="Not an owner in channel")

    # check if user isn't only owner 
    if u_id in channel_dict['owner'] and len(channel_dict['owner']) == 1:
        raise InputError(description="Only owner of channel")
    
    # remove u_id as owner
    channel_dict['owner'].remove(u_id)

    data_store.set(store)

    return {}

def channel_addowner_v1(token, channel_id, u_id):
    '''
    channel_addowner_v1: Given a valid authorised token with owner_permissions and valid channel_id makes u_id an owner of channel

    Arguments:
        token (string) - token string used to authorise and authenticate the user 
        channel_id    - id of the channel from which details are pulled 
        u_id - user_id of the one to be made an owner
        

    Exceptions:
        InputError  - Occurs when channel_id does not refer to a valid channel
        InputError  - Occurs when u_id does not refer to a valid user
        InputError - Occurs when channel_id is valid but authorised user is not a member of the channel
        InputError - When u_id is already an owner of channel
        AccessError - token has no owner permissions in channel
        AccessError - Occurs when token isn't valid 

    Return Value:
        Returns {}

    '''
    store = data_store.get()

    #check if token is valid
    auth_user_id = validate_token(token)['user_id']

    # check if channel id is valid
    if channel_id not in filter_data_store(store_list='channels',key='id'):
        raise InputError(description="Invalid channel_id")

    # check if token has owner permissions, is in owner or has global permissions
    user_dict = filter_data_store(store_list='users',key='id',value=auth_user_id)[0]
    channel_dict = filter_data_store(store_list='channels',key='id',value=channel_id)[0]
    if auth_user_id not in channel_dict['owner'] and user_dict['permission_id'] != 1:
        raise AccessError(description='User does not have owner permissions in channel')
    
    # if is global owner check that they are a member of the channel 
    if auth_user_id not in channel_dict['members']:
        raise AccessError(description='User does not have owner permissions in channel')

    # check if u_id is valid
    if u_id not in filter_data_store(store_list='users', key='id'): 
        raise InputError(description="Invalid user_id")

    # check if u_id is member of channel
    if u_id not in channel_dict['members']:
        raise InputError(description="Not a member of channel")
    
    # check if u_id already owner of channel
    if u_id in channel_dict['owner']:
        raise InputError(description='Already an owner of channel')
    
    # make u_id owner of channel 
    channel_dict['owner'].append(u_id)
    data_store.set(store)

    return {}

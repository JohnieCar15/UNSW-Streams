from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import validate_token, filter_data_store
'''
channel_invite_v1: Invites a user with ID u_id to join a channel with ID channel_id.
Arguments:
    auth_user_id (int)    - User id of the authorised user
    channel_id (int)    - Channel id of the channel the user wishes to join

Exceptions:
    InputError  - Occurs when channel_id does not refer to a valid channel
                - Occurs when the authorised user is already a member of the channel
    AccessError - Occurs when channel_id refers to a channel that is private and the
                  authorised user is not already a channel member and is not a global owner
                - Occurs when the auth_user_id passed in is not a valid id
                
Return Value:
    Returns {} on successful auth_user_id and channel_id

'''
def channel_invite_v1(auth_user_id, channel_id, u_id):
    store = data_store.get()
    
    # Checking if the auth_user_id is valid
    user_id_list = [user['id'] for user in store['users']]
    if auth_user_id not in user_id_list:
        raise AccessError("Invalid auth_user_id")

    channel_list = [channel for channel in store['channels'] if channel['id'] == channel_id]
    # Checking if the channel_id is valid
    if len(channel_list) == 0:
        raise InputError("Invalid channel_id")
    # Checking if the auth_user_id is a member of the channel
    elif auth_user_id not in channel_list[0]['members']:
        raise AccessError('Auth user is not a member of channel')
    # Checking if the u_id is valid
    elif u_id not in user_id_list:
        raise InputError("Invalid u_id")
    # Checking if the u_id is already a member of the channel
    elif u_id in channel_list[0]['members']:
        raise InputError('User already member of channel')
    else:
        channel_list[0]['members'].append(u_id)
    
    data_store.set(store)
    return {}

'''
channel_details_v1: Given a valid authroised user_id and valid channel_id displays details for that channel 

Arguments:
    auth_user_id (int)    - User id of the authorised user
    channel_id    - id of the channel from which details are pulled 
    

Exceptions:
    InputError  - Occurs when channel_id does not refer to a valid channel
    AccessError - Occurs when channel_id is valid but authorised user is not a member of the channel
    AccessError - Occurs when auth_user_id isn't valid 

Return Value:
    Returns {name, is_public, owner_members, all_members}
    

'''
def channel_details_v1(auth_user_id, channel_id):
    
    store = data_store.get()

    # check if auth_user_id is valid
    if auth_user_id not in [user['id'] for user in store['users']]:
        raise AccessError("Invalid user_id")
    
    # check if channel_id refers to a valid id
    if channel_id not in [channel['id'] for channel in store['channels']]:
        raise InputError("Invalid channel_id")

    # check if user is member of channel
    channel_dict =  [channel for channel in store['channels'] if channel_id == channel['id']][0]
    if auth_user_id not in channel_dict['members']:
        raise AccessError("Not a member of channel")

    # get variables for channel details from store['channels']
    channel_name = channel_dict['name']
    channel_is_public = channel_dict['is_public']
    channel_members = channel_dict['members']
    channel_owner_id = channel_dict['owner']
            
    # get variables for channel details - owner from store['users']
    for user in store['users']:
        if channel_owner_id == user['id']:
            owner_email = user['email']
            owner_name_f = user['name_first']
            owner_name_l = user['name_last']
            owner_handle = user['handle_str']

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
        'owner_members': [
            {
                'u_id': channel_owner_id ,
                'email': owner_email ,
                'name_first': owner_name_f ,
                'name_last': owner_name_l ,
                'handle_str': owner_handle ,
            }
        ],
        'all_members': all_members_list
    }

def channel_details_v2(token, channel_id):
    store = data_store.get()
    channel_id = int(channel_id)
    # check if token is valid
    auth_user_id = validate_token(token)
    
    # check if channel_id refers to a valid id
    channel_list = [channel['id'] for channel in store['channels']]
    if len(channel_list) == 0:
        raise InputError(description="Invalid channel_id")
    
    # check if user is member of channel
    channel_dict =  [channel for channel in store['channels'] if channel_id == channel['id']][0]
    if auth_user_id not in channel_dict['members']:
        raise AccessError(description="Not a member of channel")

    # get variables for channel details from store['channels']
    channel_name = channel_dict['name']
    channel_is_public = channel_dict['is_public']
    channel_members = channel_dict['members']
    channel_owners = channel_dict['owner']
    print(channel_owners)
    all_owners_list = []
    # get variables for channel details - owner from store['users']
    for owner in store['users']:
        print(owner['id'])
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
'''
channel_messages_v1: Given a channel_id and start, returns up to 50 messages from start to start + 50,
as well as the start and finishing indexes

Arguments:
    auth_user_id (int)    - id of a user
    channel_id (int)    - id of a channel
    start (int) - starting index of the messages to be returned
    ...

Exceptions:
    InputError  - Occurs when invalid channel id is entered
                - Occurs when start is greater than total number of messages
    AccessError - Occurs when user is not part of channel members

Return Value:
    Returns {messages, 'start', 'end'} on successful auth_user_id, channel_id and start

'''
def channel_messages_v1(auth_user_id, channel_id, start):
    store = data_store.get()

  # check if auth_user_id is valid
    if auth_user_id not in [user['id'] for user in store['users']]:
        raise AccessError("Invalid user_id")
  # Checks if channel id is valid
    if channel_id not in [channel['id'] for channel in store['channels']]:
        raise InputError("Invalid channel_id")
  # Finds the channel with the correct id
    for channel in store['channels']:
        if channel['id'] == channel_id:
            new_channel = channel
            break
  # Check if user is in channel members
    if auth_user_id not in new_channel['members']:
        raise AccessError("Invalid user_id")

    length = len(new_channel['messages']) - start
    # A negative length implies that start > length
    if length < 0:
        raise InputError("Start is greater than total number of messages")
    # Negative starts are invalid
    if start < 0:
      raise InputError("Invalid start")

    messages_dict = {}
    messages_dict['start'] = start
    # Deals with all cases
    if length == 0:
        messages_dict['end'] = -1
        messages_dict['messages'] = []
    elif length <= 50:
        messages_dict['end'] = -1
        # Create a copy of all messages from start up to final index
        messages_dict['messages'] = new_channel['messages'][start:start + length - 1]
    else:
        messages_dict['end'] = start + 50
        messages_dict['messages'] = new_channel['messages'][start:start + 49]

        
    return messages_dict

'''
channel_join_v1: Given a channel_id of a channel that the authorised user can join, adds them to that channel.
Arguments:
    auth_user_id (int)    - User id of the authorised user
    channel_id (int)    - Channel id of the channel the user wishes to join

Exceptions:
    InputError  - Occurs when channel_id does not refer to a valid channel
                - Occurs when the authorised user is already a member of the channel
    AccessError - Occurs when channel_id refers to a channel that is private and the
                  authorised user is not already a channel member and is not a global owner
                - Occurs when the auth_user_id passed in is not a valid id
                
Return Value:
    Returns {} on successful auth_user_id and channel_id

'''
def channel_join_v1(auth_user_id, channel_id):
    store = data_store.get()

    # Checking if the auth_user_id is valid
    user_list = [user for user in store['users'] if user['id'] == auth_user_id]
    if len(user_list) == 0:
        raise AccessError("Invalid user_id")

    
    channel_list = [channel for channel in store['channels'] if channel['id'] == channel_id]
    # Checking if the channel_id is valid
    if len(channel_list) == 0:
        raise InputError("Invalid channel_id")
    # Checking if the auth_user_id is already member of the channel
    elif auth_user_id in channel_list[0]['members']:
        raise InputError('User already member of channel')
    # Checking if the channel is private and the auth user is not a global owner
    elif user_list[0]['permission_id'] != 1 and not channel_list[0]['is_public']:
        raise AccessError("User cannot join private channel")
    else:
        channel_list[0]['members'].append(auth_user_id)
    
    data_store.set(store)

    return {}

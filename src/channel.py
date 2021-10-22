from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import validate_token, filter_data_store

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

    channel_list = filter_data_store(list='channels', key='id', value=channel_id)
    # Checking if the channel_id is valid
    if len(channel_list) == 0:
        raise InputError(description="Invalid channel_id")
    # Checking if the auth_user_id is a member of the channel
    elif auth_user_id not in channel_list[0]['members']:
        raise AccessError(description='Auth user is not a member of channel')
    # Checking if the u_id is valid
    elif filter_data_store(list='users', key='id', value=u_id) is None:
        raise InputError(description="Invalid u_id")
    # Checking if the u_id is already a member of the channel
    elif u_id in channel_list[0]['members']:
        raise InputError(description='User already member of channel')
    
    channel_list[0]['members'].append(u_id)
    
    data_store.set(store)
    return {}

def channel_details_v2(token, channel_id):
    '''
    channel_details_v2: Given a valid authroised token and valid channel_id displays details for that channel 

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
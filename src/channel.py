from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import validate_token, filter_data_store


# Helper function for channel_join_v2
def is_global_owner(u_id):
    user_dict = filter_data_store(list='users', key='id',value=u_id)
    return user_dict[0]['permission_id'] == 1

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

    channel_list = filter_data_store(list='channels', key='id', value=channel_id)
 
    # Checking if the channel_id is valid
    if channel_list is None:
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
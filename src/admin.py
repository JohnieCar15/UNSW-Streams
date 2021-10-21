from src.data_store import data_store
from src.error import AccessError, InputError
from src.helpers import validate_token, filter_data_store


# Helper Function
def is_global_owner(u_id):
    user_dict = filter_data_store(store='users', key='id',value=u_id)
    return user_dict['permission_id'] == 1

# Helper Function
def check_valid_permission_id(permission_id):
    if permission_id not in (1, 2):
        raise InputError(description='permission_id is invalid')

# Helper Function
def is_last_global_owner(u_id):
    global_owner_list = filter_data_store(store='users', key='permission_id', value=1)
    return len(global_owner_list) == 1 and global_owner_list[0]['id'] == u_id


def admin_userpermission_change_v1(token, u_id, permission_id):
    '''
    admin_userpermission_change_v1: 
    Given a user by their user ID, set their permissions to new permissions described by permission_id.

    Arguments:
        token (str)         - Token string used to authorise and authenticate the user
        u_id (int)          - User id of the user that the admin wishes to change
        permission_id (int) - Permission id that the admin wishes to change the user to

    Exceptions:
        InputError  - Occurs when u_id does not refer to a valid user
                    - Occurs when u_id refers to a user who is the only global owner
                      and they are being demoted to a user
                    - Occurs when permission_id is invalid
        AccessError - Occurs when the authorised user is not a global owner
                    - Occurs when the token passed in is not a valid token
                    
    Return Value:
        Returns {} on successful token and u_id
    '''
    store = data_store.get()
    # Checking that the token is valid and returning the decoded token
    auth_user_dict = validate_token(token)

    # Checking the auth user is a global owner
    if not is_global_owner(auth_user_dict['user_id']):
        raise AccessError(description='The authorised user is not a global owner')

    # Checking the u_id entered is valid
    changed_user_dict = filter_data_store(list='users', key='id', value=u_id)
    if changed_user_dict is None:
        raise InputError(description='u_id does not refer to a valid user')

    # Checking if the u_id refers to the last global owner and they are demoted
    check_valid_permission_id(permission_id)
    if is_last_global_owner(u_id) and permission_id == 2:
        raise InputError(description='u_id refers the only global owner and they are being demoted to a user')

    changed_user_dict['permission_id'] = permission_id
    
    data_store.set(store)
    return {}



    

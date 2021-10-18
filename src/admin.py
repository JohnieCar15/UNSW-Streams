from src.data_store import data_store
from src.error import AccessError, InputError
from src.helpers import validate_token, filter_data_store


# Helper Function
def is_global_owner(u_id):
    user_dict = filter_data_store(list='users', key='id',value=u_id)
    return user_dict['permission_id'] == 1

# Helper Function
def check_valid_permission_id(permission_id):
    if permission_id not in (1, 2):
        raise InputError(description='permission_id is invalid')

# Helper Function
def is_last_global_owner(u_id):
    global_owner_list = filter_data_store(list='users', key='permission_id', value=1)
    return len(global_owner_list) == 1 and global_owner_list[0]['id'] == u_id


def admin_userpermission_change_v1(token, u_id, permission_id):
    store = data_store.get()
    auth_user_dict = validate_token(token)

    if not is_global_owner(auth_user_dict['user_id']):
        raise AccessError(description='The authorised user is not a global owner')

    changed_user_dict = filter_data_store(list='users', key='id', value=u_id)
    if changed_user_dict is None:
        raise InputError(description='u_id does not refer to a valid user')

    check_valid_permission_id(permission_id)
    if is_last_global_owner(u_id) and permission_id == 2:
        raise InputError(description='u_id refers the only global owner and they are being demoted to a user')

    changed_user_dict['permission_id'] = permission_id
    
    data_store.set(store)
    return {}



    

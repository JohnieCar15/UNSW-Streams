from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import validate_token, filter_data_store, generate_new_img_id
from src import config
import re
import urllib.request
from PIL import Image

'''
user.py: This file contains all functions relating to user endpoints.

User Functions:
    - users_all_v1(token)
    - user_profile_v1(token, u_id)
    - user_profile_setname_v1(token, name_first, name_last)
    - user_profile_setemail_v1(token, email)
    - user_profile_sethandle_v1(token, handle)
    - user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end)
    - user_stats_v1(token)
    - users_stats_v1(token)
'''

regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'

def users_all_v1(token):
    '''
    users_all_v1: Returns a list of all users and their associated details.

    Arguments:
        token  - str    - token of the user

    Exceptions: 
        AccessError - Occurs when token is invalid

    Return Value:
        Returns a dictionary contains list of users
        For example: { 'users': 
            [
            {'u_id': 1, 
            'email': 'abcd@unsw.edu.au', 
            'name_first': 'name', 
            'name_last': 'name', 
            'handle_str': handle_str}, 
            ]
        }
    '''

    # Checking if token is valid
    # if token can not be decoded
    # raise AccessError(description="Invalid token")
    validate_token(token)
    # get a list of user
    store = data_store.get()

    list_of_user = []
    for user in store['users']:
            list_of_user.append(
                {
                    'u_id': user['id'],
                    'email': user['email'],
                    'name_first': user['name_first'],
                    'name_last': user['name_last'],
                    'handle_str': user['handle_str'],
                    'profile_img_url': user['profile_img_url']
                }
            )

    return {'users': list_of_user}


def user_profile_v1(token, u_id):
    '''
    users_profile_v1: For a valid user, returns information about their
                        user_id, email, first name, last name, and handle

    Arguments:
        token  - string    - token of the user
        u_id   - integer   - autg_user_id of the user

    Exceptions: 
        AccessError - Occurs when token is invalid
        InputError  - Occurs when u_id does not refer to a valid user

    Return Value:
        Returns a dictionary contains list of users
        For example: { 'user': 
            {'u_id': 1, 
            'email': 'abcd@unsw.edu.au',
            'name_first': 'name', 
            'name_last': 'name', 
            'handle_str': handle_str},
        }                     
    '''
    store = data_store.get()
    # Checking if token is valid
    # if token can not be decoded
    # raise AccessError(description="Invalid token")
    validate_token(token)
    user = [user for user in (store['users'] + store['removed_users']) if user['id'] == u_id]
    if user == []:
        raise InputError(description="Invalid u_id")

    user = user[0]
    return {'user': 
        {
        'u_id': user['id'],
        'email': user['email'],
        'name_first': user['name_first'],
        'name_last': user['name_last'],
        'handle_str': user['handle_str'],
        'profile_img_url': user['profile_img_url']
        }
    }


def user_profile_setname_v1(token, name_first, name_last):
    '''
    user_profile_setname_v1: Update the authorised user's first and last name

    Arguments:
        token       - string    - token of the user
        name_first  - string    - firstname of the user
        name_last   - string    - lastname of the user

    Exceptions: 
        AccessError - token is invalid
        InputError  - length of name_first or name_last is not
                      between 1 and 50 characters inclusive
                    
    Return Value:
        Returns {}
    '''
    
    
    # Checking if token is valid
    # if token can not be decoded
    # raise AccessError(description="Invalid token")
    u_id = validate_token(token)['user_id']
    
    if len(name_first) < 1 or len(name_first) > 50:
        raise InputError(description="Invalid name_first length")
    if len(name_last) < 1 or len(name_last) > 50:
        raise InputError(description="Invalid name_last length")

    store = data_store.get()
    for user_index in range(len(store['users'])):
        if store['users'][user_index]['id'] == u_id:
            if store['users'][user_index]['name_first'] == name_first and \
                store['users'][user_index]['name_last'] == name_last:
                raise InputError(description="same name_as previous")
            store['users'][user_index]['name_first'] = name_first
            store['users'][user_index]['name_last'] = name_last
    data_store.set(store)
    return {}

def user_profile_setemail_v1(token, email):
    '''
    user_profile_setemail_v1: Update the authorised user's first and last name

    Arguments:
        token       - string    - token of the user
        email       - string    - email of the user

    Exceptions: 
        AccessError - token is invalid
        InputError  - email entered is not a valid email (more in section 6.4)
                    - email address is already being used by another user

    Return Value:
        Returns {}
    '''


    # Checking if token is valid
    # if token can not be decoded
    # raise AccessError(description="Invalid token")
    u_id = validate_token(token)['user_id']

    # Checking if email is valid
    if not re.fullmatch(regex, email):
        raise InputError(description="Invalid email")

    email_of_current_user = filter_data_store(store_list='users', key='id', value = u_id)[0]['email']
    if email_of_current_user == email:
        raise InputError (description="email is the same as previous")

    email_list = filter_data_store(store_list='users', key='email')
    # if email_list == None:
    #    raise InputError(description="No valid email yet")
    if email in email_list:
        raise InputError (description="email is used by other user")

    store = data_store.get()
    for user_index in range(len(store['users'])):
        if store['users'][user_index]['id'] == u_id:
            store['users'][user_index]['email'] = email
    data_store.set(store)
    return {}


def user_profile_sethandle_v1(token, handle):
    '''
    user_profile_sethandle_v1: Update the authorised user's first and last name

    Arguments:
        token   - string    - token of the user
        handle  - string    - handle of the user

    Exceptions: 
        AccessError - token is invalid
        InputError  - length of handle_str is not between 3 and 20 characters inclusive
                    - handle_str contains characters that are not alphanumeric
                    - the handle is already used by another user


    Return Value:
        Returns {}
    '''

    
    # Checking if token is valid
    # if token can not be decoded
    # raise AccessError(description="Invalid token")
    u_id = validate_token(token)['user_id']

    # Checking if handle is valid
    if len(handle) < 3 or len(handle) > 20:
        raise InputError(description='Invalid handle length')
    if not handle.isalnum():
        raise InputError(description='handle contains char that are not alphanumeric')


    handle_of_current_user = filter_data_store(store_list='users', key='id', value = u_id)[0]['handle_str']
    if handle_of_current_user == handle:
        raise InputError (description="handle is the same as previous")

    handle_list = filter_data_store(store_list='users', key='handle_str')
    # if handle_list == None:
    #   raise InputError(description="No valid handle_str yet")
    if handle in handle_list:
        raise InputError (description="handle_str is used by other user")

    store = data_store.get()
    for user_index in range(len(store['users'])):
        if store['users'][user_index]['id'] == u_id:
            store['users'][user_index]['handle_str'] = handle
    data_store.set(store)
    return {}

def user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end):
    '''
    user_profile_uploadphoto_v1: Changes a users profile photo, given a valid image url

    Arguments:
        token (str)     - token of a user
        img_url (str)   - img_url that the user wants to upload
        x_start (int)   - x-dimension start for image crop
        y_start (int)   - y-dimension start for image crop
        x_end (int)     - x-dimension end for image crop
        y_end (int)     - y-dimension end for image crop

    Exceptions:
        InputError      - Occurs when img_url returns an HTTP status other than 200
                        - Occurs when any of x_start, y_start, x_end, y_end are not within the dimensions of the image at the URL
                        - Occurs when x_end is less than x_start or y_end is less than y_start
                        - Occurs when image uploaded is not a JPG

    Return Value:
        Returns {}
    '''  
    # Checking token is valid
    u_id = validate_token(token)['user_id']

    # Checking correct file type
    if not img_url.endswith(".jpg") and not img_url.endswith(".jpeg"):
        raise InputError(description='Image uploaded is not a JPG')

    # Checking correct dimensions
    if x_end < x_start:
        raise InputError(description='x_end is less than x_start')
    if y_end < y_start:
        raise InputError(description='y_end is less than y_start')
    if x_start < 0 or y_start < 0:
        raise InputError(description='Given dimensions are not within the dimensions of the image at the URL')

    img_id = generate_new_img_id()
    img_path = f"src/images/{img_id}.jpg"

    try:
        urllib.request.urlretrieve(img_url, img_path)
    except Exception as e:
        raise InputError(description='Invalid img_url') from e


    image_object = Image.open(img_path)
    width, height = image_object.size

    if x_end > width or y_end > height:
        raise InputError(description='Given dimensions are not within the dimensions of the image at the URL')

    cropped_image = image_object.crop((x_start, y_start, x_end, y_end))
    cropped_image.save(img_path)

    store = data_store.get()
    
    user = filter_data_store(store_list='users', key='id', value=u_id)[0]
    user['profile_img_url'] = f"{config.url}images/{img_id}.jpg"

    data_store.set(store)

    return {}
    
def user_stats_v1(token):
    '''
    user_stats_v1: Fetches the required statistics about this user's use of UNSW Streams.

    Arguments:
        token   - string    - token of the user

    Exceptions: 
        AccessError - token is invalid

    Return Value:
        Returns {
            'user_stats': {
                channels_joined: [{num_channels_joined, time_stamp}],
                dms_joined: [{num_dms_joined, time_stamp}], 
                messages_sent: [{num_messages_sent, time_stamp}], 
                involvement_rate: sum(num_channels_joined, num_dms_joined, num_msgs_sent)/
                                    sum(num_channels, num_dms, num_msgs). 
                    # If the denominator is 0, involvement should be 0. 
                    # If the involvement is greater than 1, it should be capped at 1.
            }
        }
    '''
    store = data_store.get()
    # Checking if token is valid
    # if token can not be decoded
    # raise AccessError(description="Invalid token")
    u_id = validate_token(token)['user_id']
    user = [user for user in (store['users'] + store['removed_users']) if user['id'] == u_id]

    user = user[0]
    channels_joined = user['channels_joined']
    dms_joined = user['dms_joined']
    messages_sent = user['messages_sent']
    

    num_channels_joined = channels_joined[-1]['num_channels_joined']
    num_dms_joined = dms_joined[-1]['num_dms_joined']
    num_messages_sent = messages_sent[-1]['num_messages_sent']
    store = data_store.get()

    num_channels = store['channels_exist'][-1]['num_channels_exist']
    num_dms = store['dms_exist'][-1]['num_dms_exist']
    num_messages = store['messages_exist'][-1]['num_messages_exist']
    if num_channels + num_dms + num_messages == 0:
        involvement_rate = 0
    else: 
        involvement_rate = (num_channels_joined + num_dms_joined + num_messages_sent)/(num_channels + num_dms + num_messages)
    
    return {
        'user_stats': {
            'channels_joined': channels_joined,
            'dms_joined': dms_joined,
            'messages_sent': messages_sent,
            'involvement_rate': min(involvement_rate, 1)
        }
    }

def users_stats_v1(token):
    '''
    users_stats_v1: Fetches the required statistics about the use of UNSW Streams.

    Arguments:
        token   - string    - token of the user

    Exceptions: 
        AccessError - token is invalid

    Return Value:
        Returns {
            'users_stats':  {
                channels_exist: [{num_channels_exist, time_stamp}], 
                dms_exist: [{num_dms_exist, time_stamp}], 
                messages_exist: [{num_messages_exist, time_stamp}], 
                utilization_rate: num_users_who_have_joined_at_least_one_channel_or_dm / num_users
            }
        }
    '''
    store = data_store.get()
    # Checking if token is valid
    # if token can not be decoded
    # raise AccessError(description="Invalid token")
    validate_token(token)['user_id']

    # get num_users and num_users_in_cahnnel_or_dm and calculate utilization_rate
    num_users = len(store['users'])
    num_users_who_have_joined_at_least_one_channel_or_dm = len(store['users_in_channel_or_dm'])
    utilization_rate = num_users_who_have_joined_at_least_one_channel_or_dm / num_users
    return {
        'workspace_stats': {
            'channels_exist': store['channels_exist'],
            'dms_exist': store['dms_exist'],
            'messages_exist':  store['messages_exist'],
            'utilization_rate': utilization_rate
        }
    }

from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import validate_token
import datetime

def message_send_v1(token, channel_id, message):
    store = data_store.get()

    # check if token is valid
    auth_user_id = validate_token(token)['user_id']

    # Checks if channel id is valid
    if channel_id not in [channel['id'] for channel in store['channels']]:
        raise InputError(description="Invalid channel_id")

    channel_dict = [channel for channel in store['channels'] if channel['id'] == channel_id][0]

    if auth_user_id not in channel_dict['members']:
        raise AccessError(description="Not a member of channel")

    if len(message) < 1 or len(message) > 1000:
        raise InputError(description="Invalid message")

    new_message = {}
    new_message['message_id'] = len(store['messages']) + 1
    new_message['u_id'] = auth_user_id
    new_message['message'] = message
    new_message['time_created'] = datetime.datetime.utcnow()

    channel_dict['messages'].insert(0, new_message)

    new_message['channel_id'] = channel_id

    store['messages'].insert(0, new_message)

    data_store.set(store)

    return new_message['message_id']

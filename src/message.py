from src.data_store import data_store
from src.error import InputError, AccessError
from src.helpers import validate_token

def message_edit_v1(token, message_id, message):
    store = data_store.get()

    # check if token is valid
    auth_user_id = validate_token(token)['user_id']

    # Checks if message exists
    # Contains extra field "channel_id"
    message_dict = [message for message in store['messages'] if message_id == message['message_id']][0]

    if not message_dict:
        return InputError(description="Invalid message")

    # Checks which channel the message is sent in and finds that message
    channel_dict = [channel for channel in store['channels'] if message_dict['channel_id'] == channel['id']][0]
    selected_message = [message for message in channel_dict['messages'] if message_id == message['message_id']][0]

    # Checks if user is part of that channel
    if auth_user_id not in channel_dict['members']:
        return AccessError(description="Not a member of channel")
    
    if auth_user_id != message_dict['u_id'] and auth_user_id != channel_dict['owner']:
        return AccessError(description="Permission denied")

    if len(message) > 1000:
        return InputError(description="Message is too long")

    if len(message) == 0:
        store['messages'].remove(message_dict)
        channel_dict['messages'].remove(selected_message)
    else:
        message_dict['message'] = message
        selected_message['message'] = message

    data_store.set(store)

    return {}
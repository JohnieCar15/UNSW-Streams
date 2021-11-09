import pytest
import requests
import time
from datetime import datetime
from src import config
from src.error import AccessError, InputError


@pytest.fixture
def notifications_get_url():
    return config.url + 'notifications/get/v1'

@pytest.fixture
def clear_and_register():
    requests.delete(config.url + 'clear/v1')

    auth_register_input1 = {
        'email':'user1@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last': 'Last'
    }
    user1_payload = requests.post(config.url + 'auth/register/v2', json=auth_register_input1).json()

    user_profile_input1 = {
        'token': user1_payload['token'],
        'u_id': user1_payload['auth_user_id']
    }
    user1_profile = requests.get(config.url + 'user/profile/v1', params=user_profile_input1).json()['user']

    auth_register_input2 = {
        'email':'user2@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last': 'Last'
    }
    user2_payload = requests.post(config.url + 'auth/register/v2', json=auth_register_input2).json()


    channels_create_input = {
        'token': user1_payload['token'],
        'name': 'Channel',
        'is_public': True
    }
    channel_id = requests.post(config.url + 'channels/create/v2', json=channels_create_input).json()['channel_id']

    dm_create_input = {
        'token': user1_payload['token'],
        'u_ids': []
    }
    dm_id = requests.post(config.url + 'dm/create/v1', json=dm_create_input).json()['dm_id']

    return {
        'user1_token': user1_payload['token'],
        'user1_id': user1_payload['auth_user_id'],
        'user1_handle': user1_profile['handle_str'],
        'user2_token': user2_payload['token'],
        'user2_id': user2_payload['auth_user_id'],
        'channel_id': channel_id,
        'dm_id': dm_id
        }


# Testing the error case of passing in an invalid token
def test_invalid_token(notifications_get_url, clear_and_register):
    # Creating an invalid token (empty string)
    invalid_token = ''

    r = requests.get(notifications_get_url, params={'token': invalid_token})
    assert r.status_code == AccessError.code


def test_tagging_in_message_send(notifications_get_url, clear_and_register):
    user_token = clear_and_register['user1_token']
    user_handle = clear_and_register['user1_handle']
    channel_id = clear_and_register['channel_id']

    message_string = f'Hello @{user_handle}, welcome to Streams!'
    requests.post(config.url + 'message/send/v1', json={
        'token': user_token,
        'channel_id': channel_id,
        'message': message_string
    }).json()['message_id']

    r = requests.get(notifications_get_url, params={'token': user_token})
    notification = r.json()['notifications'][0]
    assert r.status_code == 200
    assert notification['channel_id'] == channel_id
    assert notification['dm_id'] == -1
    assert notification['notification_message'] == "firstlast tagged you in Channel: Hello @firstlast, we"

def test_tagging_in_message_senddm(notifications_get_url, clear_and_register):
    user_token = clear_and_register['user1_token']
    user_handle = clear_and_register['user1_handle']
    dm_id = clear_and_register['dm_id']

    message_string = f'Hello @{user_handle}, welcome to Streams!'
    requests.post(config.url + 'message/senddm/v1', json={
        'token': user_token,
        'dm_id': dm_id,
        'message': message_string
    }).json()['message_id']

    r = requests.get(notifications_get_url, params={'token': user_token})
    notification = r.json()['notifications'][0]
    assert r.status_code == 200
    assert notification['channel_id'] == -1
    assert notification['dm_id'] == dm_id
    assert notification['notification_message'] == "firstlast tagged you in firstlast: Hello @firstlast, we"

def test_tagging_in_message_sendlater(notifications_get_url, clear_and_register):
    user_token = clear_and_register['user1_token']
    user_handle = clear_and_register['user1_handle']
    channel_id = clear_and_register['channel_id']

    message_string = f'Hello @{user_handle}, welcome to Streams!'
    requests.post(config.url + 'message/sendlater/v1', json={
        'token': user_token,
        'channel_id': channel_id,
        'message': message_string,
        'time_sent': int(datetime.utcnow().timestamp()) + 1
    }).json()['message_id']

    time.sleep(1)

    r = requests.get(notifications_get_url, params={'token': user_token})
    notification = r.json()['notifications'][0]
    assert r.status_code == 200
    assert notification['channel_id'] == channel_id
    assert notification['dm_id'] == -1
    assert notification['notification_message'] == "firstlast tagged you in Channel: Hello @firstlast, we"

def test_tagging_in_message_sendlaterdm(notifications_get_url, clear_and_register):
    user_token = clear_and_register['user1_token']
    user_handle = clear_and_register['user1_handle']
    dm_id = clear_and_register['dm_id']

    message_string = f'Hello @{user_handle}, welcome to Streams!'
    requests.post(config.url + 'message/sendlaterdm/v1', json={
        'token': user_token,
        'dm_id': dm_id,
        'message': message_string,
        'time_sent': int(datetime.utcnow().timestamp()) + 1
    }).json()['message_id']

    time.sleep(1)

    r = requests.get(notifications_get_url, params={'token': user_token})
    notification = r.json()['notifications'][0]
    assert r.status_code == 200
    assert notification['channel_id'] == -1
    assert notification['dm_id'] == dm_id
    assert notification['notification_message'] == "firstlast tagged you in firstlast: Hello @firstlast, we"

def test_tagging_in_message_edit(notifications_get_url, clear_and_register):
    user_token = clear_and_register['user1_token']
    user_handle = clear_and_register['user1_handle']
    channel_id = clear_and_register['channel_id']

    message_id = requests.post(config.url + 'message/send/v1', json={
        'token': user_token,
        'channel_id': channel_id,
        'message': 'message'
    }).json()['message_id']

    message_string = f'Hello @{user_handle}, welcome to Streams!'
    requests.put(config.url + 'message/edit/v1', json={
        'token': user_token,
        'message_id': message_id,
        'message': message_string
    })

    r = requests.get(notifications_get_url, params={'token': user_token})
    notification = r.json()['notifications'][0]
    assert r.status_code == 200
    assert notification['channel_id'] == channel_id
    assert notification['dm_id'] == -1
    assert notification['notification_message'] == "firstlast tagged you in Channel: Hello @firstlast, we"

def test_tagging_in_message_share(notifications_get_url, clear_and_register):
    user_token = clear_and_register['user1_token']
    user_handle = clear_and_register['user1_handle']
    channel_id = clear_and_register['channel_id']

    message_id = requests.post(config.url + 'message/send/v1', json={
        'token': user_token,
        'channel_id': channel_id,
        'message': 'message'
    }).json()['message_id']

    message_string = f'Hello @{user_handle}, welcome to Streams!'
    requests.post(config.url + 'message/share/v1', json={
        'token': user_token,
        'og_message_id': message_id,
        'message': message_string,
        'channel_id': channel_id,
        'dm_id': -1
    })

    r = requests.get(notifications_get_url, params={'token': user_token})
    notification = r.json()['notifications'][0]
    assert r.status_code == 200
    assert notification['channel_id'] == channel_id
    assert notification['dm_id'] == -1
    assert notification['notification_message'] == "firstlast tagged you in Channel: Hello @firstlast, we"

def test_reacting_to_channel_message(notifications_get_url, clear_and_register):
    user_token = clear_and_register['user1_token']
    channel_id = clear_and_register['channel_id']

    message_id = requests.post(config.url + 'message/send/v1', json={
        'token': user_token,
        'channel_id': channel_id,
        'message': 'message'
    }).json()['message_id']

    requests.post(config.url + 'message/react/v1', json={
        'token': user_token,
        'message_id': message_id,
        'react_id': 1
    })

    r = requests.get(notifications_get_url, params={'token': user_token})
    notification = r.json()['notifications'][0]
    assert r.status_code == 200
    assert notification['channel_id'] == channel_id
    assert notification['dm_id'] == -1
    assert notification['notification_message'] == "firstlast reacted to your message in Channel"

def test_reacting_to_dm_message(notifications_get_url, clear_and_register):
    user_token = clear_and_register['user1_token']
    dm_id = clear_and_register['dm_id']

    message_id = requests.post(config.url + 'message/senddm/v1', json={
        'token': user_token,
        'dm_id': dm_id,
        'message': 'message'
    }).json()['message_id']

    requests.post(config.url + 'message/react/v1', json={
        'token': user_token,
        'message_id': message_id,
        'react_id': 1
    })

    r = requests.get(notifications_get_url, params={'token': user_token})
    notification = r.json()['notifications'][0]
    assert r.status_code == 200
    assert notification['channel_id'] == -1
    assert notification['dm_id'] == dm_id
    assert notification['notification_message'] == "firstlast reacted to your message in firstlast"

def test_inviting_to_channel(notifications_get_url, clear_and_register):
    auth_user_token = clear_and_register['user1_token']
    user_token = clear_and_register['user2_token']
    user_id = clear_and_register['user2_id']
    channel_id = clear_and_register['channel_id']

    requests.post(config.url + 'channel/invite/v2', json={
        'token': auth_user_token,
        'channel_id': channel_id,
        'u_id': user_id
    })

    r = requests.get(notifications_get_url, params={'token': user_token})
    notification = r.json()['notifications'][0]
    assert r.status_code == 200
    assert notification['channel_id'] == channel_id
    assert notification['dm_id'] == -1
    assert notification['notification_message'] == "firstlast added you to Channel"

def test_inviting_to_dm(notifications_get_url, clear_and_register):
    auth_user_token = clear_and_register['user1_token']
    user_token = clear_and_register['user2_token']
    user_id = clear_and_register['user2_id']

    dm_id = requests.post(config.url + 'dm/create/v1', json={
        'token': auth_user_token,
        'u_ids': [user_id]
    }).json()['dm_id']

    r = requests.get(notifications_get_url, params={'token': user_token})
    notification = r.json()['notifications'][0]
    assert r.status_code == 200
    assert notification['channel_id'] == -1
    assert notification['dm_id'] == dm_id
    assert notification['notification_message'] == "firstlast added you to firstlast, firstlast0"

def test_over_20_notifications(notifications_get_url, clear_and_register):
    user_token = clear_and_register['user1_token']
    user_handle = clear_and_register['user1_handle']
    channel_id = clear_and_register['channel_id']

    for i in reversed(range(25)):
        message_string = f'@{user_handle} {i}'
        requests.post(config.url + 'message/send/v1', json={
            'token': user_token,
            'channel_id': channel_id,
            'message': message_string
        }).json()['message_id']

    r = requests.get(notifications_get_url, params={'token': user_token})
    notifications = r.json()['notifications']
    assert r.status_code == 200
    assert len(notifications) == 20

    for index, notification in enumerate(notifications):
        assert notification['channel_id'] == channel_id
        assert notification['dm_id'] == -1
        assert notification['notification_message'] == f"firstlast tagged you in Channel: @firstlast {index}"


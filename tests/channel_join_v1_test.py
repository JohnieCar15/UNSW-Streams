import pytest

from src.channel import channel_join_v1, channel_details_v1
from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.other import clear_v1
from src.error import InputError, AccessError

@pytest.mark.skip
def test_general():
    clear_v1()
    creator_id = auth_register_v1('creator@gmail.com', 'password', 'First', 'Last')['auth_user_id']
    user_id = auth_register_v1('user@gmail.com', 'password', 'First', 'Last')['auth_user_id']
    channel_id = channels_create_v1(creator_id, 'Channel', True)['channel_id']

    channel_join_v1(user_id, channel_id)
    channel_members = channel_details_v1(user_id, channel_id)['all_members']
    channel_members_ids = [user['u_id'] for user in channel_members]

    assert user_id in channel_members_ids


def test_invalid_user_id():
    clear_v1()
    valid_user_id = auth_register_v1('valid@gmail.com', 'password', 'First', 'Last')['auth_user_id']
    valid_channel_id = channels_create_v1(valid_user_id, 'Channel', True)['channel_id']

    invalid_user_id = valid_user_id + 1
    with pytest.raises(AccessError):
        channel_join_v1(invalid_user_id, valid_channel_id)

def test_invalid_channel_id():
    clear_v1()
    valid_user_id = auth_register_v1('valid@gmail.com', 'password', 'First', 'Last')['auth_user_id']
    valid_channel_id = channels_create_v1(valid_user_id, 'Channel', True)['channel_id']

    invalid_channel_id = valid_channel_id + 1
    with pytest.raises(InputError):
        channel_join_v1(valid_user_id, invalid_channel_id)

def test_all_ids_invalid():
    clear_v1()
    valid_user_id = auth_register_v1('valid@gmail.com', 'password', 'First', 'Last')['auth_user_id']
    valid_channel_id = channels_create_v1(valid_user_id, 'Channel', True)['channel_id']

    invalid_user_id = valid_user_id + 1
    invalid_channel_id = valid_channel_id + 1
    with pytest.raises(AccessError):
        channel_join_v1(invalid_user_id, invalid_channel_id)

def test_duplicate():
    clear_v1()
    user_id = auth_register_v1('valid@gmail.com', 'password', 'First', 'Last')['auth_user_id']
    channel_id = channels_create_v1(user_id, 'Channel', True)['channel_id']

    with pytest.raises(InputError):
        channel_join_v1(user_id, channel_id)

#### Assumption that iteration1 does not incorporate global owners ####

def test_private_channel_without_global_owner():
    clear_v1()
    creator_id = auth_register_v1('creator@gmail.com', 'password', 'First', 'Last')['auth_user_id']
    user_id = auth_register_v1('valid@gmail.com', 'password', 'First', 'Last')['auth_user_id']
    private_channel_id = channels_create_v1(creator_id, 'Channel', False)['channel_id']

    with pytest.raises(AccessError):
        channel_join_v1(user_id, private_channel_id)


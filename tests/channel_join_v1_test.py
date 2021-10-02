import pytest

from src.channel import channel_join_v1, channel_details_v1
from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.other import clear_v1
from src.error import InputError, AccessError


@pytest.fixture
def clear_and_register():
    clear_v1()
    user1_id = auth_register_v1('user1@gmail.com', 'password', 'First', 'Last')['auth_user_id']
    user2_id = auth_register_v1('user2@gmail.com', 'password', 'First', 'Last')['auth_user_id']
    return {'user1_id': user1_id, 'user2_id': user2_id}

# Testing the general case of a user joining a public channel
def test_general(clear_and_register):
    creator_id = clear_and_register['user1_id']
    user_id = clear_and_register['user2_id']
    channel_id = channels_create_v1(creator_id, 'Channel', True)['channel_id']

    channel_join_v1(user_id, channel_id)

    channel_members = channel_details_v1(creator_id, channel_id)['all_members']
    channel_members_ids = [user['u_id'] for user in channel_members]

    assert user_id in channel_members_ids

# Testing the error case of passing an invalid auth_user_id
def test_invalid_user_id(clear_and_register):
    valid_user_id = clear_and_register['user1_id']
    valid_channel_id = channels_create_v1(valid_user_id, 'Channel', True)['channel_id']

    # Generating an invalid id that doesn't match existing ids
    invalid_user_id = valid_user_id + 1
    if invalid_user_id == clear_and_register['user2_id']:
        invalid_user_id += 1

    with pytest.raises(AccessError):
        channel_join_v1(invalid_user_id, valid_channel_id)

# Testing the error case of passing an invalid channel_id
def test_invalid_channel_id(clear_and_register):
    valid_user_id = clear_and_register['user1_id']
    valid_channel_id = channels_create_v1(valid_user_id, 'Channel', True)['channel_id']

    # Generating an invalid id that doesn't match existing ids
    invalid_channel_id = valid_channel_id + 1

    with pytest.raises(InputError):
        channel_join_v1(valid_user_id, invalid_channel_id)

# Testing the error case of passing an invalid auth_user_id and channel_id
def test_all_ids_invalid(clear_and_register):
    valid_user_id = clear_and_register['user1_id']
    valid_channel_id = channels_create_v1(valid_user_id, 'Channel', True)['channel_id']
    
    # Generating invalid ids that don't match exising ids
    invalid_channel_id = valid_channel_id + 1
    invalid_user_id = valid_user_id + 1
    if invalid_user_id == clear_and_register['user2_id']:
        invalid_user_id += 1

    with pytest.raises(AccessError):
        channel_join_v1(invalid_user_id, invalid_channel_id)

# Testing the error case of a user joining a channel twice
def test_duplicate(clear_and_register):
    user_id = clear_and_register['user1_id']
    channel_id = channels_create_v1(user_id, 'Channel', True)['channel_id']

    with pytest.raises(InputError):
        channel_join_v1(user_id, channel_id)

# Testing the error case of a non-global owner joining a private channel
def test_private_channel_without_global_owner(clear_and_register):
    creator_id = clear_and_register['user1_id']
    user_id = clear_and_register['user2_id']
    private_channel_id = channels_create_v1(creator_id, 'Channel', False)['channel_id']

    with pytest.raises(AccessError):
        channel_join_v1(user_id, private_channel_id)


# Testing the general case of a global owner joining a private channel
def test_private_channel_with_global_owner(clear_and_register):
    global_owner_id = clear_and_register['user1_id']
    creator_id = clear_and_register['user2_id']
    private_channel_id = channels_create_v1(creator_id, 'Channel', False)['channel_id']

    channel_join_v1(global_owner_id, private_channel_id)

    channel_members = channel_details_v1(creator_id, private_channel_id)['all_members']
    channel_members_ids = [user['u_id'] for user in channel_members]

    assert global_owner_id in channel_members_ids

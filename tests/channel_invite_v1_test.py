import pytest

from src.channel import channel_invite_v1, channel_join_v1 ,channel_details_v1
from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.other import clear_v1
from src.error import InputError, AccessError

@pytest.mark.skip
def test_public_channel_invite():
    clear_v1()
    auth_id = auth_register_v1('auth@gmail.com', 'password', 'First', 'Last')['auth_user_id']
    invitee_id = auth_register_v1('user@gmail.com', 'password', 'First', 'Last')['auth_user_id']
    public_channel_id = channels_create_v1(auth_id, 'Channel', True)['channel_id']
    
    channel_invite_v1(auth_id, public_channel_id, invitee_id)

    channel_members = channel_details_v1(auth_id, public_channel_id)['all_members']
    channel_members_ids = [user['u_id'] for user in channel_members]

    assert invitee_id in channel_members_ids

@pytest.mark.skip
def test_private_channel_invite():
    clear_v1()
    auth_id = auth_register_v1('auth@gmail.com', 'password', 'First', 'Last')['auth_user_id']
    invitee_id = auth_register_v1('user@gmail.com', 'password', 'First', 'Last')['auth_user_id']
    private_channel_id = channels_create_v1(auth_id, 'Channel', False)['channel_id']
    
    channel_invite_v1(auth_id, private_channel_id, invitee_id)

    channel_members = channel_details_v1(auth_id, private_channel_id)['all_members']
    channel_members_ids = [user['u_id'] for user in channel_members]

    assert invitee_id in channel_members_ids


def test_invalid_auth_id():
    clear_v1()
    valid_auth_id = auth_register_v1('auth@gmail.com', 'password', 'First', 'Last')['auth_user_id']
    valid_invitee_id = auth_register_v1('user@gmail.com', 'password', 'First', 'Last')['auth_user_id']
    valid_channel_id = channels_create_v1(valid_auth_id, 'Channel', False)['channel_id']

    invalid_auth_id = valid_auth_id + 1
    if invalid_auth_id == valid_invitee_id:
        invalid_auth_id += 1

    with pytest.raises(AccessError):
        channel_invite_v1(invalid_auth_id, valid_channel_id, valid_invitee_id)

def test_invalid_invitee_id():
    clear_v1()
    valid_auth_id = auth_register_v1('auth@gmail.com', 'password', 'First', 'Last')['auth_user_id']
    valid_invitee_id = auth_register_v1('user@gmail.com', 'password', 'First', 'Last')['auth_user_id']
    valid_channel_id = channels_create_v1(valid_auth_id, 'Channel', False)['channel_id']

    invalid_invitee_id = valid_invitee_id + 1
    if invalid_invitee_id == valid_auth_id:
        invalid_invitee_id += 1

    with pytest.raises(InputError):
        channel_invite_v1(valid_auth_id, valid_channel_id, invalid_invitee_id)

def test_invalid_channel_id():
    clear_v1()
    valid_auth_id = auth_register_v1('valid@gmail.com', 'password', 'First', 'Last')['auth_user_id']
    valid_invitee_id = auth_register_v1('user@gmail.com', 'password', 'First', 'Last')['auth_user_id']
    valid_channel_id = channels_create_v1(valid_auth_id, 'Channel', True)['channel_id']

    invalid_channel_id = valid_channel_id + 1
    with pytest.raises(InputError):
        channel_invite_v1(valid_auth_id, invalid_channel_id, valid_invitee_id)

def test_all_ids_invalid():
    clear_v1()
    valid_auth_id = auth_register_v1('auth@gmail.com', 'password', 'First', 'Last')['auth_user_id']
    valid_invitee_id = auth_register_v1('user@gmail.com', 'password', 'First', 'Last')['auth_user_id']
    valid_channel_id = channels_create_v1(valid_auth_id, 'Channel', False)['channel_id']

    invalid_channel_id = valid_channel_id + 1

    invalid_auth_id = valid_auth_id + 1
    if invalid_auth_id == valid_invitee_id:
        invalid_auth_id += 1

    invalid_invitee_id = valid_invitee_id + 1
    while invalid_invitee_id == valid_auth_id or invalid_invitee_id == invalid_auth_id:
        invalid_invitee_id += 1

    with pytest.raises(AccessError):
        channel_invite_v1(invalid_auth_id, invalid_channel_id, invalid_invitee_id)


def test_duplicate_invite():
    clear_v1()
    auth_id = auth_register_v1('auth@gmail.com', 'password', 'First', 'Last')['auth_user_id']
    invitee_id = auth_register_v1('user@gmail.com', 'password', 'First', 'Last')['auth_user_id']
    channel_id = channels_create_v1(auth_id, 'Channel', False)['channel_id']

    channel_invite_v1(auth_id, channel_id, invitee_id)
    with pytest.raises(InputError):
        channel_invite_v1(auth_id, channel_id, invitee_id)

def test_inviter_not_in_channel():
    clear_v1()
    auth_id = auth_register_v1('auth@gmail.com', 'password', 'First', 'Last')['auth_user_id']
    inviter_id = auth_register_v1('user1@gmail.com', 'password', 'First', 'Last')['auth_user_id']
    invitee_id = auth_register_v1('user2@gmail.com', 'password', 'First', 'Last')['auth_user_id']
    channel_id = channels_create_v1(auth_id, 'Channel', False)['channel_id']

    with pytest.raises(AccessError):
        channel_invite_v1(inviter_id, channel_id, invitee_id)


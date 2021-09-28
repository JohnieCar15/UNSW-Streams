import pytest

from src.error import AccessError
from src.other import clear_v1
from src.auth import auth_register_v1, auth_login_v1
from src.channel import channel_invite_v1
from src.channels import channels_listall_v1, channels_create_v1

# this test file defined function:
# test_invalid_user_id
# test_valid_user_not_in_any_channel
# test_owner_of_one_public_channel
# test_member_of_one_public_channel
# test_owner_of_one_private_channel
# test_member_of_one_private_channel
# test_complex_case


# this fuction will create two channels: public_0 and private_0
# and register four users: 
# public_0 owner, public_0, member
# private_0 owner, private_0 member
@pytest.fixture
def clear_then_crete_public0_and_private0():
    clear_v1()
    # register public_0_owner and create channel public_0
    public_0_owner = auth_register_v1("0000@unsw.edu.au", "password", "firstname0","lastname0")['auth_user_id']
    public_0 = channels_create_v1(public_0_owner, "public_0", True)

    # register public_0_member and join channel public_0
    public_0_member = auth_register_v1("0001@unsw.edu.au", "password", "firstname1","lastname1")['auth_user_id']
    channel_invite_v1(public_0_owner, public_0, public_0_member)

    # register private_0_owner and create channel private_0
    private_0_owner = auth_register_v1("0002@unsw.edu.au", "password", "firstname2","lastname2")['auth_user_id']
    private_0 = channels_create_v1(private_0_owner, "private_0", False)
    
    # register public_0_member and invite to channel public_0    
    private_0_member = auth_register_v1("0003@unsw.edu.au", "password", "firstname3","lastname3")['auth_user_id']
    channel_invite_v1(private_0_owner, private_0, private_0_member)

# test invalid u_id and this should raise AccessError 
def test_invalid_user_id():
    clear_v1()
    # uid is invalid when there is no any valid uid
    id_invalid = 100
    with pytest.raises(AccessError):
        channels_listall_v1(id_invalid)
    # when in_valid is passed into channels_listall_v1, AccessError should be raised
    # To avoid that is coidcidence by no creation for channels, further test is carried
    clear_v1()
    id_invalid = 100
    public_0_owner = auth_register_v1("0000@unsw.edu.au", "password", "firstname0","lastname0")['auth_user_id']
    # since there is only one valid uid for "public_0_owner"
    # to get a invalid uid, just make it different with "public_0_owner"
    while id_invalid == public_0_owner:  # avoid id_invalid == id_onwer
        id_invalid += 1
    
    public_channel_0 = channels_create_v1(public_0_owner, "public_0", True)
    with pytest.raises(AccessError):
        channels_listall_v1(id_invalid)


def test_valid_user_but_no_channels_have_been_created():
    clear_v1()
    user_in_no_channels = auth_register_v1("0004@unsw.edu.au", "password", "firstname4","lastname4")['auth_user_id']
    assert channels_listall_v1(user_in_no_channels) == {'channels': []}

def test_normal_case(clear_then_crete_public0_and_private0):
    uid = auth_login_v1("0000@unsw.edu.au", "password")['auth_user_id']
    assert channels_listall_v1(uid) == {'channels': [
        {'channel_id': 1, 'name': 'public_0'}, 
        {'channel_id': 2, 'name': 'private_0'},
        ]}

def test_complex_case(clear_then_crete_public0_and_private0):
    clear_v1()
    # register public_0_owner and create channel public_0
    public_0_owner = auth_register_v1("0000@unsw.edu.au", "password", "firstname0","lastname0")['auth_user_id']
    public_0 = channels_create_v1(public_0_owner, "public_0", True)

    # register public_0_member and join channel public_0
    public_0_member = auth_register_v1("0001@unsw.edu.au", "password", "firstname1","lastname1")['auth_user_id']
    channel_invite_v1(public_0_owner, public_0, public_0_member)

    # register private_0_owner and create channel private_0
    private_0_owner = auth_register_v1("0002@unsw.edu.au", "password", "firstname2","lastname2")['auth_user_id']
    private_0 = channels_create_v1(private_0_owner, "private_0", False)
    
    # register public_0_member and invite to channel public_0    
    private_0_member = auth_register_v1("0003@unsw.edu.au", "password", "firstname3","lastname3")['auth_user_id']
    channel_invite_v1(private_0_owner, private_0, private_0_member)
    
    # create a user who is not in any channel
    user_in_no_channels = auth_register_v1("0004@unsw.edu.au", "password", "firstname4","lastname4")['auth_user_id']

    # register public_1_owner and create channel public_1
    public_1_owner = auth_register_v1("0005@unsw.edu.au", "password", "firstname5","lastname5")['auth_user_id']
    public_1 = channels_create_v1(public_1_owner, "public_1", True)

    # register public_2_owner and create channel public_2
    public_2_owner = auth_register_v1("0006@unsw.edu.au", "password", "firstname6","lastname6")['auth_user_id']
    public_2 = channels_create_v1(public_2_owner, "public_2", True)

    # register private_1_owner and create channel private_1
    private_1_owner = auth_register_v1("0007@unsw.edu.au", "password", "firstname7","lastname7")['auth_user_id']
    private_1 = channels_create_v1(private_1_owner, "private_1", False)

    member_in_all_channels = auth_register_v1("0008@unsw.edu.au", "password", "firstname8","lastname8")['auth_user_id']

    # member_in_all_channels is in all channels
    channel_invite_v1(public_0_owner, public_0, member_in_all_channels)
    channel_invite_v1(private_0_owner, private_0, member_in_all_channels)
    channel_invite_v1(public_1_owner, public_1, member_in_all_channels)
    channel_invite_v1(private_1_owner, private_1, member_in_all_channels)
    channel_invite_v1(public_2_owner, public_2, member_in_all_channels)

    channel_invite_v1(public_1_owner, public_1, public_0_owner)
    # public_0_owner is in public_0, public_1

    channel_invite_v1(public_1_owner, public_1, public_0_member)
    channel_invite_v1(public_2_owner, public_2, public_0_member)
    channel_invite_v1(private_1_owner, private_1, public_0_member)
    # public_0_member is in public_0, public_1, public_2, private_1

    # private_0_owner is in private_0

    channel_invite_v1(private_1_owner, private_1, private_0_member)
    # private_0_member is in private_0, private_1

    channel_invite_v1(private_0_owner, private_0, public_1_owner)
    # public_1_owner is in public_1, private_0

    channel_invite_v1(public_1_owner, public_1, public_2_owner)    
    channel_invite_v1(private_1_owner, private_1, public_2_owner)
    # public_2_owner is in public_2, public_1, private_1


    channel_invite_v1(public_0_owner, public_0, private_1_owner)
    channel_invite_v1(private_0_owner, private_0, private_1_owner)
    # private_1_owner is in private_1, public_0, private_0
    
    # test if the function works for different types of users
    assert channels_listall_v1(user_in_no_channels) == {'channels': [
        {'channel_id': 1, 'name': 'public_0'}, 
        {'channel_id': 2, 'name': 'private_0'},
        {'channel_id': 3, 'name': 'public_1'},
        {'channel_id': 4, 'name': 'public_2'},
        {'channel_id': 5, 'name': 'private_1'},
        ]}

    assert channels_listall_v1(member_in_all_channels) == {'channels': [
        {'channel_id': 1, 'name': 'public_0'}, 
        {'channel_id': 2, 'name': 'private_0'},
        {'channel_id': 3, 'name': 'public_1'},
        {'channel_id': 4, 'name': 'public_2'},
        {'channel_id': 5, 'name': 'private_1'},
        ]}

    assert channels_listall_v1(public_0_owner) == {'channels': [
        {'channel_id': 1, 'name': 'public_0'}, 
        {'channel_id': 2, 'name': 'private_0'},
        {'channel_id': 3, 'name': 'public_1'},
        {'channel_id': 4, 'name': 'public_2'},
        {'channel_id': 5, 'name': 'private_1'},
        ]}

    assert channels_listall_v1(public_0_member) == {'channels': [
        {'channel_id': 1, 'name': 'public_0'}, 
        {'channel_id': 2, 'name': 'private_0'},
        {'channel_id': 3, 'name': 'public_1'},
        {'channel_id': 4, 'name': 'public_2'},
        {'channel_id': 5, 'name': 'private_1'},
        ]}

    assert channels_listall_v1(private_0_owner) == {'channels': [
        {'channel_id': 1, 'name': 'public_0'}, 
        {'channel_id': 2, 'name': 'private_0'},
        {'channel_id': 3, 'name': 'public_1'},
        {'channel_id': 4, 'name': 'public_2'},
        {'channel_id': 5, 'name': 'private_1'},
        ]}

    assert channels_listall_v1(private_0_member) == {'channels': [
        {'channel_id': 1, 'name': 'public_0'}, 
        {'channel_id': 2, 'name': 'private_0'},
        {'channel_id': 3, 'name': 'public_1'},
        {'channel_id': 4, 'name': 'public_2'},
        {'channel_id': 5, 'name': 'private_1'},
        ]}

    assert channels_listall_v1(public_1_owner) == {'channels': [
        {'channel_id': 1, 'name': 'public_0'}, 
        {'channel_id': 2, 'name': 'private_0'},
        {'channel_id': 3, 'name': 'public_1'},
        {'channel_id': 4, 'name': 'public_2'},
        {'channel_id': 5, 'name': 'private_1'},
        ]}

    assert channels_listall_v1(public_2_owner) == {'channels': [
        {'channel_id': 1, 'name': 'public_0'}, 
        {'channel_id': 2, 'name': 'private_0'},
        {'channel_id': 3, 'name': 'public_1'},
        {'channel_id': 4, 'name': 'public_2'},
        {'channel_id': 5, 'name': 'private_1'},
        ]}

    assert channels_listall_v1(private_1_owner) == {'channels': [
        {'channel_id': 1, 'name': 'public_0'}, 
        {'channel_id': 2, 'name': 'private_0'},
        {'channel_id': 3, 'name': 'public_1'},
        {'channel_id': 4, 'name': 'public_2'},
        {'channel_id': 5, 'name': 'private_1'},
        ]}
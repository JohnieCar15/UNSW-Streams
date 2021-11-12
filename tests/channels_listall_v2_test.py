import pytest
import requests
from src import config
from src.error import AccessError

'''
channels_listall_v2_test.py: All functions related to testing the channels_listall_v2 function
'''

# Help functions:

# Sorts list of channels by channel_id
def sort_list(channel_list):
    return sorted(channel_list, key=lambda k: k['channel_id'])


# regiseter a user and return {"token": token, "auth_user_id": u_id}
def user_register(email, password, name_first, name_last):
    input = {
        "email" : email,
        "password" : password,
        "name_first" : name_first,
        "name_last" : name_last
    }
    return requests.post(config.url + 'auth/register/v2', json=input).json()

# create a channel and return {"channel_id": channel_id}
def channel_create(creator, name, is_public):
    input = {
        "token": creator["token"],
        'name': name,
        "is_public": is_public
    }
    return requests.post(config.url + 'channels/create/v2', json=input).json()

# invite a user to channel
def channel_invite(inviter, channel, invitee):
    input = {
        "token": inviter["token"],
        "channel_id": channel["channel_id"],
        "u_id": invitee["auth_user_id"]
    }
    requests.post(config.url + 'channel/invite/v2', json=input)

# invite a user to channel, return {channels that user belongs to}
def channels_listall(user):
    return requests.get(config.url + 'channels/listall/v2', params={"token": user["token"]}).json()


# this function will create two channels: public_0 and private_0
# and register four users: 
# public_0 owner, public_0, member,
# private_0 owner, private_0 member,
# then return all users and channels created by it

@pytest.fixture
def clear_then_create_public0_and_private0():
    requests.delete(config.url + 'clear/v1')
    # register public_0_owner and create channel public_0

    public_0_owner = user_register("0000@unsw.edu.au", "password", "firstname0", "lastname0")
    public_0 = channel_create(public_0_owner, "public_0", True)

    # register public_0_member and invite to channel public_0
    public_0_member = user_register("0001@unsw.edu.au", "password", "firstname1", "lastname1")
    channel_invite(public_0_owner, public_0, public_0_member)

    # register private_0_owner and create channel private_0
    private_0_owner = user_register("0002@unsw.edu.au", "password", "firstname2", "lastname2")
    private_0 = channel_create(private_0_owner, "private_0", False)
    
    # register public_0_member and invite to channel private_0
    private_0_member = user_register("0003@unsw.edu.au", "password", "firstname3","lastname3")
    channel_invite(private_0_owner, private_0, private_0_member)

    return {
        "public_0": public_0,
        "public_0_owner": public_0_owner,
        "public_0_member": public_0_member,

        "private_0": private_0,
        "private_0_owner": private_0_owner,
        "private_0_member": private_0_member
        }


# Test Case:

# this test file defined function:
# test_invalid_user_id
# test_valid_user_not_in_any_channel
# test_owner_of_one_public_channel
# test_member_of_one_public_channel
# test_owner_of_one_private_channel
# test_member_of_one_private_channel
# test_complex_case


# test invalid token and this should raise AccessError
def test_invalid_user_id():
    requests.delete(config.url + 'clear/v1')
    assert requests.get(config.url + 'channels/listall/v2', params={"token": "invalid"}).status_code == AccessError.code


def test_valid_user_but_no_channels_have_been_created():
    # create a user without any channels have be created
    requests.delete(config.url + 'clear/v1')
    user_in_no_channels = user_register("0000@unsw.edu.au", "password", "firstname0", "lastname0")
    assert channels_listall(user_in_no_channels) == {'channels': []}


def test_normal_case(clear_then_create_public0_and_private0):
    # the the sorted function will return the list of dictionary sorted by "channel_id"
    public0_and_private0 = clear_then_create_public0_and_private0
    public_0_owner = public0_and_private0["public_0_owner"]
    public_0 = public0_and_private0["public_0"]
    private_0 = public0_and_private0["private_0"]
    expect_result = sort_list([{'channel_id': public_0["channel_id"], 'name': 'public_0'}, {'channel_id': private_0["channel_id"], 'name': 'private_0'}])
    assert sort_list(channels_listall(public_0_owner)['channels']) == expect_result


def test_complex_case(clear_then_create_public0_and_private0):
    # By fixture get the data of public_0 and private_0
    public0_and_private0 = clear_then_create_public0_and_private0

    public_0_owner = public0_and_private0["public_0_owner"]
    public_0_member = public0_and_private0["public_0_member"]
    public_0 = public0_and_private0["public_0"]

    private_0_owner = public0_and_private0["private_0_owner"]
    private_0_member = public0_and_private0["private_0_member"]
    private_0 = public0_and_private0["private_0"]

    # create a user who is not in any channel
    user_in_no_channels = user_register("0004@unsw.edu.au", "password", "firstname4", "lastname4")


    # register public_1_owner and create channel public_1
    public_1_owner = user_register("0005@unsw.edu.au", "password", "firstname5", "lastname5")
    public_1 = channel_create(public_1_owner, "public_1", True)
    

    # register public_2_owner and create channel public_2
    public_2_owner = user_register("0006@unsw.edu.au", "password", "firstname6", "lastname6")
    public_2 = channel_create(public_2_owner, "public_2", True)
    

    # register private_1_owner and create channel private_1
    private_1_owner = user_register("0007@unsw.edu.au", "password", "firstname7", "lastname7")
    private_1 = channel_create(private_1_owner, "private_1", False)
    
    member_in_all_channels = user_register("0008@unsw.edu.au", "password", "firstname8","lastname8")

    # member_in_all_channels is in all channels
    channel_invite(public_0_owner, public_0, member_in_all_channels)
    channel_invite(private_0_owner, private_0, member_in_all_channels)
    channel_invite(public_1_owner, public_1, member_in_all_channels)
    channel_invite(private_1_owner, private_1, member_in_all_channels)
    channel_invite(public_2_owner, public_2, member_in_all_channels)

    channel_invite(public_1_owner, public_1, public_0_owner)
    # public_0_owner is in public_0, public_1

    channel_invite(public_1_owner, public_1, public_0_member)
    channel_invite(public_2_owner, public_2, public_0_member)
    channel_invite(private_1_owner, private_1, public_0_member)
    # public_0_member is in public_0, public_1, public_2, private_1

    # private_0_owner is in private_0

    channel_invite(private_1_owner, private_1, private_0_member)
    # private_0_member is in private_0, private_1

    channel_invite(private_0_owner, private_0, public_1_owner)
    # public_1_owner is in public_1, private_0

    channel_invite(public_1_owner, public_1, public_2_owner)    
    channel_invite(private_1_owner, private_1, public_2_owner)
    # public_2_owner is in public_2, public_1, private_1


    channel_invite(public_0_owner, public_0, private_1_owner)
    channel_invite(private_0_owner, private_0, private_1_owner)
    # private_1_owner is in private_1, public_0, private_0
    
    # test if the function works for different types of users\
    list_of_all_channels = [
        {'channel_id': public_0["channel_id"], 'name': 'public_0'}, 
        {'channel_id': private_0["channel_id"], 'name': 'private_0'},
        {'channel_id': public_1["channel_id"], 'name': 'public_1'},
        {'channel_id': private_1["channel_id"], 'name': 'private_1'},
        {'channel_id': public_2["channel_id"], 'name': 'public_2'},
        ]

    # sorted list_of_all_channels
    list_of_all_channels = sort_list(list_of_all_channels)

    assert sort_list(channels_listall(user_in_no_channels)['channels']) == list_of_all_channels
    assert sort_list(channels_listall(member_in_all_channels)['channels']) == list_of_all_channels
    assert sort_list(channels_listall(public_0_owner)['channels']) == list_of_all_channels
    assert sort_list(channels_listall(public_0_member)['channels']) == list_of_all_channels
    assert sort_list(channels_listall(private_0_owner)['channels']) == list_of_all_channels
    assert sort_list(channels_listall(private_0_member)['channels']) == list_of_all_channels
    assert sort_list(channels_listall(public_1_owner)['channels']) == list_of_all_channels
    assert sort_list(channels_listall(public_2_owner)['channels']) == list_of_all_channels
    assert sort_list(channels_listall(private_1_owner)['channels']) == list_of_all_channels

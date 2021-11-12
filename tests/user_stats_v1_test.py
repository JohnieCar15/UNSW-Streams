from datetime import datetime, timezone
import requests
import time
from src import config
from src.error import AccessError
'''
user_stats_v1_test.py: All functions related to testing the user_stats_v1 function

the test function:
    test_invalid_user_token()
    test_no_channel_dm_message()
    test_involvement_greater_than_1()
    test_general(), more information in the function doc of test_general()
    test_message_sendlater_in_channel_dm_and_standup_send()

helper functions:
    user_stats(user)
    get_input(num_channels_joined, num_dms_joined, num_messages_sent, \
            num_channels_exist, num_dms_exist, num_messages_exist)
    check_related_num_of_all_key_and_timestamp_for_specific_key(user, user_input, keys)
    check_all_key_of_user_stats_not_including_timestamp(user, user_input)
    check_involvement_rate(user, input)
    check_num_and_time_stamp(user, key, num, check_time=False)

    user_register(email, password, name_first, name_last)
    channel_create(creator, name, is_public)
    channel_invite(inviter, channel, invitee)
    channel_join(user,channel)
    channel_leave(user, channel)
    dm_create(creator, list_of_invitee)
    dm_leave(user, dm)
    dm_remove(user, dm)
    message_send(user, channel, message)
    message_senddm(user, dm, message)
    message_remove(user, message)
    message_share(user, og_message, new_message, channel_id=-1, dm_id=-1)
    message_sendlater(user, channel, message, time_sent)
    message_sendlaterdm(user, dm, message, time_sent)
    standup_start(user, channel, length)
    standup_send(user, channel, message)
'''

# Test Case:
def test_invalid_user_token():
    '''
    test invalid token, this shouldd raise AccessError
    '''
    requests.delete(config.url + 'clear/v1')
    assert requests.get(config.url + 'user/stats/v1', params={'token': 'invalid_token'}).status_code == AccessError.code

def test_no_channel_dm_message():
    '''
    test when sum(num_channels_exist, num_dms_exist, num_messages_exist) == 0
    expect_result = { 
        'user_stats': {
            'channels_joined': [{'num_channels_joined': 0, 'time_stamp': }],
            'dms_joined': [{'num_dms_joined': 0, 'time_stamp': }], 
            'messages_sent': [{'num_messages_sent': 0, 'time_stamp': }], 
            'involvement_rate': 0
        }
    }
    '''
    # make sure this test is not affected by message_sendlater(dm) and standup_send
    time.sleep(3)
    # clear data_store
    requests.delete(config.url + 'clear/v1')

    # register a user
    user0 = user_register('0000@unsw.edu.au', 'password', 'firstname0', 'lastname0')
    input_0 = get_input(num_channels_joined=0, num_dms_joined=0, num_messages_sent=0,\
                        num_channels_exist=0, num_dms_exist=0, num_messages_exist=0)
    # compare the returned dictionary of user_stats and the calculated value
    keys = ['channels_joined', 'dms_joined', 'messages_sent']
    check_related_num_of_all_key_and_timestamp_for_specific_key(user=user0, user_input=input_0, keys=keys)


def test_involvement_greater_than_1():
    '''
    test  involvement is greater than 1 (by deleting messages)
    involvement_rate will be capped at 1
    '''
    # clear data_store
    requests.delete(config.url + 'clear/v1')
    num_channels_exist = 0
    num_dms_exist = 0
    num_messages_exist = 0

    # register a user
    user0 = user_register('0000@unsw.edu.au', 'password', 'firstname0', 'lastname0')
    
    # create a channel
    public_0 = channel_create(user0, 'public_0', True)
    num_channels_exist += 1

    # call user/stats/v1 in the helper function, and check returned value
    user0_input = get_input(1, 0, 0, num_channels_exist, num_dms_exist, num_messages_exist)
    check_related_num_of_all_key_and_timestamp_for_specific_key(user=user0, user_input=user0_input, keys=['channels_joined'])

    # send a message in the channel, 
    message_0 = message_send(user0, public_0, '1')
    num_messages_exist += 1

    # call user/stats/v1 in the helper function, and check returned value
    user0_input = get_input(1, 0, 1, num_channels_exist, num_dms_exist, num_messages_exist)
    check_related_num_of_all_key_and_timestamp_for_specific_key(user=user0, user_input=user0_input, keys=['messages_sent'])

    # send second message in the channel,
    message_1 = message_send(user0, public_0, '1')
    num_messages_exist += 1
    user0_input = get_input(1, 0, 2, num_channels_exist, num_dms_exist, num_messages_exist)
    check_related_num_of_all_key_and_timestamp_for_specific_key(user=user0, user_input=user0_input, keys=['messages_sent'])

    # then remove first message
    message_remove(user0, message_0)
    num_messages_exist -= 1
    user0_input = get_input(1, 0, 2, num_channels_exist, num_dms_exist, num_messages_exist)
    check_related_num_of_all_key_and_timestamp_for_specific_key(user=user0, user_input=user0_input, keys=['messages_sent'])

    # remove second message, compare the final result, involvement_rate is capeed to be 1
    message_remove(user0, message_1)
    num_messages_exist -= 1
    user0_input = get_input(1, 0, 2, num_channels_exist, num_dms_exist, num_messages_exist)
    check_related_num_of_all_key_and_timestamp_for_specific_key(user=user0, user_input=user0_input, keys=['messages_sent'])


    # then do the same test to dm
    requests.delete(config.url + 'clear/v1')
    num_channels_exist = 0
    num_dms_exist = 0
    num_messages_exist = 0

    user0 = user_register('0000@unsw.edu.au', 'password', 'firstname0', 'lastname0')
    user1 = user_register('0001@unsw.edu.au', 'password', 'firstname1', 'lastname1')

    # create a dm
    dm_0 = dm_create(user0, [user1])
    num_dms_exist += 1
    user0_input = get_input(0, 1, 0, num_channels_exist, num_dms_exist, num_messages_exist)
    check_related_num_of_all_key_and_timestamp_for_specific_key(user=user0, user_input=user0_input, keys=['dms_joined', 'messages_sent'])


    user1_input = get_input(0, 1, 0, num_channels_exist, num_dms_exist, num_messages_exist)
    check_related_num_of_all_key_and_timestamp_for_specific_key(user=user1, user_input=user1_input, keys=['dms_joined', 'messages_sent'])
    
    # send a message in the dm_0 by user_0, then remove it
    message_0 = message_senddm(user0, dm_0, '1')
    num_messages_exist += 1
    user0_input = get_input(0, 1, 1, num_channels_exist, num_dms_exist, num_messages_exist)
    user1_input = get_input(0, 1, 0, num_channels_exist, num_dms_exist, num_messages_exist)
    check_related_num_of_all_key_and_timestamp_for_specific_key(user=user0, user_input=user0_input, keys=['messages_sent'])
    check_all_key_of_user_stats_not_including_timestamp(user1, user1_input)

    #remove this message
    message_remove(user0, message_0)
    num_messages_exist -= 1
    user0_input = get_input(0, 1, 1, num_channels_exist, num_dms_exist, num_messages_exist)
    user1_input = get_input(0, 1, 0, num_channels_exist, num_dms_exist, num_messages_exist)
    check_all_key_of_user_stats_not_including_timestamp(user0, user0_input)
    check_all_key_of_user_stats_not_including_timestamp(user1, user1_input)

def test_general():
    '''
    This is a large test it show the behaviour of user_stats after the functions below is called: 
        auth_register,
        channel/dm_create,
        channel_join/invite/leave,
        dm_remove, dm_leave
        message_send, message_senddm, message_remove
        message_sendlater, message_sendlaterdm,
        message_share
        standup_start_v1 standup_send_v1

    And most function has be tested in test_involvement_greater_than_1() above,
    Now we will forcus on: 
        channel_join/invite/leave,
        dm_remove, dm_leave
        message_sendlater, message_sendlaterdm
        message_share
        standup_start_v1 standup_send_v1
    '''
    # clear the data_store
    requests.delete(config.url + 'clear/v1')
    num_channels_exist = 0
    num_dms_exist = 0
    num_messages_exist = 0

    # register user0
    user0 = user_register('0000@unsw.edu.au', 'password', 'firstname0', 'lastname0')

    # create channel public_0
    public_0 = channel_create(user0, 'public_0', True)
    num_channels_exist += 1

    # register public_0_member and invite to channel public_0
    user1 = user_register('0001@unsw.edu.au', 'password', 'firstname1', 'lastname1')
    channel_join(user1, public_0)

    # register private_0_owner and create channel private_0
    user2 = user_register('0002@unsw.edu.au', 'password', 'firstname2', 'lastname2')
    private_0 = channel_create(user2, 'private_0', False)
    num_channels_exist += 1
    
    # invite user1 to private_0, check the time_stamp of 'channels_joined' for user1
    channel_invite(user2, private_0, user1)

    # test user_stats
    input0 = get_input(1, 0, 0, num_channels_exist, num_dms_exist, num_messages_exist)
    input1 = get_input(2, 0, 0, num_channels_exist, num_dms_exist, num_messages_exist)
    input2 = get_input(1, 0, 0, num_channels_exist, num_dms_exist, num_messages_exist)
    check_all_key_of_user_stats_not_including_timestamp(user0, input0)
    check_related_num_of_all_key_and_timestamp_for_specific_key(user=user1, user_input=input1, keys=['channels_joined'])
    check_all_key_of_user_stats_not_including_timestamp(user2, input2)

    # test user1 leave the channel 'public_0', check the time_stamp of 'channels_joined' for user1
    channel_leave(user1, public_0)
    input1 = get_input(1, 0, 0, num_channels_exist, num_dms_exist, num_messages_exist)
    check_related_num_of_all_key_and_timestamp_for_specific_key(user=user1, user_input=input1, keys=['channels_joined'])

    # test user1 rejoin the channel 'public_0' and send two message,
    # check the time_stamp of 'messages_sent' for user0
    channel_join(user1, public_0)
    message_0 = message_send(user1, public_0, '0')
    num_messages_exist += 1
    input1 = get_input(2, 0, 1, num_channels_exist, num_dms_exist, num_messages_exist)
    check_related_num_of_all_key_and_timestamp_for_specific_key(user=user1, user_input=input1, keys=['channels_joined'])

    message_send(user1, public_0, '1')
    num_messages_exist += 1
    input1 = get_input(2, 0, 2, num_channels_exist, num_dms_exist, num_messages_exist)
    check_related_num_of_all_key_and_timestamp_for_specific_key(user=user1, user_input=input1, keys=['messages_sent'])

    # test user1 share message0 to private_0
    message_share(user1, message_0, '0', channel_id=private_0['channel_id'], dm_id=-1)
    num_messages_exist += 1
    input1 = get_input(2, 0, 3, num_channels_exist, num_dms_exist, num_messages_exist)
    check_related_num_of_all_key_and_timestamp_for_specific_key(user=user1, user_input=input1, keys=['messages_sent'])

    # test user0 send a message in 'public_0', check the time_stamp of 'messages_sent' for user0
    message_send(user0, public_0, '2')
    num_messages_exist += 1
    input0 = get_input(1, 0, 1, num_channels_exist, num_dms_exist, num_messages_exist)
    check_related_num_of_all_key_and_timestamp_for_specific_key(user=user0, user_input=input0, keys=['messages_sent'])

    # delete message_0 (the first message sent by user1)
    message_remove(user0, message_0)
    num_messages_exist -= 1
    input0 = get_input(1, 0, 1, num_channels_exist, num_dms_exist, num_messages_exist)
    check_all_key_of_user_stats_not_including_timestamp(user0, input0)
    input1 = get_input(2, 0, 3, num_channels_exist, num_dms_exist, num_messages_exist)
    check_all_key_of_user_stats_not_including_timestamp(user1, input1)
    input2 = get_input(1, 0, 0, num_channels_exist, num_dms_exist, num_messages_exist)
    check_all_key_of_user_stats_not_including_timestamp(user2, input2)

    # now start dm test
    # create a dm including user0 aand user2, check the time_stamp of 'dms_joined'
    dm_0 = dm_create(user0, [user2])
    num_dms_exist += 1
    input0 = get_input(1, 1, 1, num_channels_exist, num_dms_exist, num_messages_exist)
    check_related_num_of_all_key_and_timestamp_for_specific_key(user=user0, user_input=input0, keys=['dms_joined'])
    input1 = get_input(2, 0, 3, num_channels_exist, num_dms_exist, num_messages_exist)
    check_all_key_of_user_stats_not_including_timestamp(user1, input1)
    input2 = get_input(1, 1, 0, num_channels_exist, num_dms_exist, num_messages_exist)
    check_related_num_of_all_key_and_timestamp_for_specific_key(user=user2, user_input=input2, keys=['dms_joined'])


    # user2 send a message in the dm, then remove it, check the time_stamp of 'messages_sent'
    message_0 = message_senddm(user2, dm_0, '0')
    num_messages_exist += 1
    input2 = get_input(1, 1, 1, num_channels_exist, num_dms_exist, num_messages_exist)
    check_related_num_of_all_key_and_timestamp_for_specific_key(user=user2, user_input=input2, keys=['messages_sent'])

    # remove this message
    message_remove(user2, message_0)
    num_messages_exist -= 1
    input0 = get_input(1, 1, 1, num_channels_exist, num_dms_exist, num_messages_exist)
    check_all_key_of_user_stats_not_including_timestamp(user0, input0)
    input1 = get_input(2, 0, 3, num_channels_exist, num_dms_exist, num_messages_exist)
    check_all_key_of_user_stats_not_including_timestamp(user1, input1)
    input2 = get_input(1, 1, 1, num_channels_exist, num_dms_exist, num_messages_exist)
    check_all_key_of_user_stats_not_including_timestamp(user2, input2)

    # user2 leave the dm_0, check the time_stamp of 'dms_joined'
    dm_leave(user2, dm_0)
    input2 = get_input(1, 0, 1, num_channels_exist, num_dms_exist, num_messages_exist)
    check_related_num_of_all_key_and_timestamp_for_specific_key(user=user2, user_input=input2, keys=['dms_joined'])

    # remove the dm_0,
    # check the time_stamp of 'dms_joined' for user0 (the only uesr in this dm before it is removed)
    dm_remove(user0, dm_0)
    num_dms_exist -= 1
    input0 = get_input(1, 0, 1, num_channels_exist, num_dms_exist, num_messages_exist)
    check_related_num_of_all_key_and_timestamp_for_specific_key(user=user0, user_input=input0, keys=['dms_joined'])
    input1 = get_input(2, 0, 3, num_channels_exist, num_dms_exist, num_messages_exist)
    check_all_key_of_user_stats_not_including_timestamp(user1, input1)
    input2 = get_input(1, 0, 1, num_channels_exist, num_dms_exist, num_messages_exist)
    check_all_key_of_user_stats_not_including_timestamp(user2, input2)


    # the untested functions now are:
    #   message_sendlater, message_sendlaterdm
    #   standup_start standup_send

def test_message_sendlaterin_channel_dm_and_standup_send():
    '''
    test the left functions: 
        message_sendlater, message_sendlaterdm
        standup_start standup_send
    '''
    # reset data_store
    requests.delete(config.url + 'clear/v1')
    num_channels_exist = 0
    num_dms_exist = 0
    num_messages_exist = 0

    # register two users
    user0 = user_register('0000@unsw.edu.au', 'password', 'firstname0', 'lastname0')
    user1 = user_register('0001@unsw.edu.au', 'password', 'firstname1', 'lastname1')

    # create a dm
    dm_0 = dm_create(user0, [user1])
    num_dms_exist += 1

    # test message sendlater dm by user0, check user_stats
    message_sendlaterdm(user0, dm_0, '0', int(datetime.now(timezone.utc).timestamp()) + 1)
    time.sleep(2)
    num_messages_exist += 1
    input0 = get_input(0, 1, 1, num_channels_exist, num_dms_exist, num_messages_exist)
    check_related_num_of_all_key_and_timestamp_for_specific_key(user=user0, user_input=input0, keys=['messages_sent'])
 
 
    # create channel public_0
    public_0 = channel_create(user0, 'public_0', True)
    num_channels_exist += 1

    # join user1 to channel public_0
    channel_join(user1, public_0)
    
    # test message send later in channel by user0, check user_stats
    message_sendlater(user0, public_0, '1', int(datetime.now(timezone.utc).timestamp()) + 1)
    time.sleep(2)
    num_messages_exist += 1
    input0 = get_input(1, 1, 2, num_channels_exist, num_dms_exist, num_messages_exist)
    check_related_num_of_all_key_and_timestamp_for_specific_key(user=user0, user_input=input0, keys=['messages_sent'])

    # test standup_send
    # user0 start a standup in channel public_0
    standup_start(user0, public_0, length=2)

    # both user0 and user1 send two message
    # before the standup ending, 
    #       the messages_exist and message_sent by user1 and user2
    # after the standup ending, 
    #       messages_exist += 1, message_sent by user1 += 1
    #       message_sent by user2 unchanged
    standup_send(user0, public_0, '2')
    standup_send(user0, public_0, '3')
    standup_send(user1, public_0, '4')
    standup_send(user1, public_0, '5')
    input0 = get_input(1, 1, 2, num_channels_exist, num_dms_exist, num_messages_exist)
    check_related_num_of_all_key_and_timestamp_for_specific_key(user=user0, user_input=input0, keys=[])
    input1 = get_input(1, 1, 0, num_channels_exist, num_dms_exist, num_messages_exist)
    check_related_num_of_all_key_and_timestamp_for_specific_key(user=user1, user_input=input1, keys=[])

    # waiting the end of standup, check user_stats
    time.sleep(3)
    num_messages_exist += 1

    input0 = get_input(1, 1, 3, num_channels_exist, num_dms_exist, num_messages_exist)
    check_related_num_of_all_key_and_timestamp_for_specific_key(user=user0, user_input=input0, keys=['messages_sent'])
    input1 = get_input(1, 1, 0, num_channels_exist, num_dms_exist, num_messages_exist)
    check_related_num_of_all_key_and_timestamp_for_specific_key(user=user1, user_input=input1, keys=[])



# Help functions:

def user_stats(user):
    '''
    return user stats
    '''
    return requests.get(config.url + 'user/stats/v1', params={'token': user['token']}).json()

def get_input(num_channels_joined, num_dms_joined, num_messages_sent, num_channels_exist, num_dms_exist, num_messages_exist):
    '''
    helper function to get data of user to be input of other helper functions:
        check_all_key_of_user_stats_not_including_timestamp()
        check_num_and_time_stamp()
        check_involvement_rate()
    '''
    return {
        'num_channels_joined': num_channels_joined,
        'num_dms_joined': num_dms_joined,
        'num_messages_sent': num_messages_sent,
        'num_channels_exist': num_channels_exist,
        'num_dms_exist': num_dms_exist,
        'num_messages_exist': num_messages_exist
    }

def check_related_num_of_all_key_and_timestamp_for_specific_key(user, user_input, keys):
    '''
    check_all_key_of_user_stats_not_including_timestamp also with the involvement_rate:
        so num_channels_joined, num_dms_joined, num_messages_sent is checked
    then check the time_stamp of specific_key
    '''
    check_all_key_of_user_stats_not_including_timestamp(user, user_input)
    # for example: after a message is sent, only the time_stamp of message needed to be check
    # keys == [message_sent], num_message_sent can be obtained in the user_input,
    # then it wiill be compare with that in the returned value of user_stats
    for key in keys:
        num = user_input['num_'+ key]
        check_num_and_time_stamp(user, key, num, check_time=True)


def check_all_key_of_user_stats_not_including_timestamp(user, user_input):
    '''
    As it's name: to check involvement_rate and 'channels_joined', 'dms_joined', 'messages_sent'
    It won't check the timestamp because it can only get the latest timestamp for the last command,
    but that won't change all the timestamp of the three keys, so this work is done by:
        check_num_and_time_stamp()
    '''
    # call user_stats and compare the returned value with expected value in user_input
    check_involvement_rate(user, user_input)
    key_list = ['channels_joined', 'dms_joined', 'messages_sent']
    for key in key_list:
        check_num_and_time_stamp(user, key = key, num = user_input['num_' + key])

def check_involvement_rate(user, input):
    '''
    check involvement_rate
    involvement_rate = sum(num_channels_joined, num_dms_joined, num_messages_sent)/sum(num_channels_exist, num_dms_exist, num_messages_exist)
    If the denominator is 0, involvement should be 0.
    If the involvement is greater than 1, it should be capped at 1.
    '''
    num_channels_joined = input['num_channels_joined']
    num_dms_joined = input['num_dms_joined']
    num_messages_sent = input['num_messages_sent']
    num_channels_exist = input['num_channels_exist']
    num_dms_exist = input['num_dms_exist']
    num_messages_exist = input['num_messages_exist']

    return_dict = user_stats(user)
    # if denominator is 0, check if the involvement is 0, and return
    if num_channels_exist + num_dms_exist + num_messages_exist == 0:
        assert return_dict['user_stats']['involvement_rate'] == 0
        return

    # check the involvement return by user_stats and expeected value calculated here
    expected_involvement = (num_channels_joined + num_dms_joined + num_messages_sent)/(num_channels_exist + num_dms_exist + num_messages_exist)
    expected_involvement = min(1,expected_involvement)
    assert return_dict['user_stats']['involvement_rate'] == expected_involvement


def check_num_and_time_stamp(user, key, num, check_time=False):
    '''
    check num of channel/dm/message and time_stamp returned by user_stats

    the defalut check_time (Boolean) is False, for 
        check_all_key_of_user_stats_not_including_timestamp
    check_time (Boolean) should be true, when it is called by 
        check_related_num_of_all_key_and_timestamp_for_specific_key
    '''
    timestamp_now = int(datetime.now(timezone.utc).timestamp())
    return_dict = user_stats(user)
    assert return_dict['user_stats'][key][-1]['num_' + key] == num
    if check_time:
        assert return_dict['user_stats'][key][-1]['time_stamp'] - timestamp_now < 2

def user_register(email, password, name_first, name_last):
    '''
    register a user and return {'token': token, 'auth_user_id': u_id}
    '''
    input = {
        'email': email,
        'password': password,
        'name_first': name_first,
        'name_last': name_last
    }
    return requests.post(config.url + 'auth/register/v2', json=input).json()


def channel_create(creator, name, is_public):
    '''
    create a channel and return {'channel_id': channel_id}
    '''
    input = {
        'token': creator['token'],
        'name': name,
        'is_public': is_public
    }
    return requests.post(config.url + 'channels/create/v2', json=input).json()


def channel_invite(inviter, channel, invitee):
    '''
    invite a user to channel
    '''
    input = {
        'token': inviter['token'],
        'channel_id': channel['channel_id'],
        'u_id': invitee['auth_user_id']
    }
    requests.post(config.url + 'channel/invite/v2', json=input)


def channel_join(user,channel):
    '''
    user join channel by channel_id
    '''
    input = {
        'token': user['token'],
        'channel_id': channel['channel_id'],
    }
    requests.post(config.url + 'channel/join/v2', json=input)


def channel_leave(user, channel):
    '''
    leave a channel
    '''
    input = {
        'token': user['token'],
        'channel_id': channel['channel_id'],
    }
    requests.post(config.url + 'channel/leave/v1', json=input)


def dm_create(creator, list_of_invitee):
    '''
    create a dm and return {'dm_id': dm_id}
    '''
    input = {
        'token': creator['token'],
        'u_ids': [user['auth_user_id'] for user in list_of_invitee]
    }
    return requests.post(config.url + 'dm/create/v1', json=input).json()


def dm_leave(user, dm):
    '''
    leave a dm
    '''
    input = {
        'token': user['token'],
        'dm_id': dm['dm_id']
    }
    requests.post(config.url + 'dm/leave/v1', json=input)


def dm_remove(user, dm):
    '''
    delete the dm
    '''
    input = {
        'token': user['token'],
        'dm_id': dm['dm_id']
    }
    requests.delete(config.url + 'dm/remove/v1', json=input)


def message_send(user, channel, message):
    '''
    send a message in specified channel, return {'message_id': message_id}
    '''
    input = {
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': message,
    }
    return requests.post(config.url + 'message/send/v1', json=input).json()


def message_senddm(user, dm, message):
    '''
    send a message in specified dm, return {'message_id': message_id}
    '''
    input = {
        'token': user['token'],
        'dm_id': dm['dm_id'],
        'message': message,
    }
    return requests.post(config.url + 'message/senddm/v1', json=input).json()


def message_remove(user, message):
    '''
    remove a message with specified message_id
    '''
    input = {
        'token': user['token'],
        'message_id': message['message_id'],
    }
    requests.delete(config.url + 'message/remove/v1', json=input)

def message_share(user, og_message, new_message, channel_id=-1, dm_id=-1):
    '''
    helper function for shareing message
    '''
    message_share_input = {
        'token': user['token'],
        'og_message_id': og_message['message_id'],
        'message': "1",
        'channel_id': channel_id,
        'dm_id': dm_id
    }
    return requests.post(config.url + '/message/share/v1', json=message_share_input).json()


def message_sendlater(user, channel, message, time_sent):
    '''
    helper function for message_sendlater
    '''
    message_sendlater_input = {
        'token' : user['token'],
        'channel_id' : channel['channel_id'],
        'message' : message,
        'time_sent' : time_sent
    }
    return requests.post(config.url + '/message/sendlater/v1', json=message_sendlater_input).json()


def message_sendlaterdm(user, dm, message, time_sent):
    '''
    helper function for message_sendlaterdm
    '''
    message_sendlaterdm_input = {
        'token' : user['token'],
        'dm_id' : dm['dm_id'],
        'message' : message,
        'time_sent' : time_sent
    }
    return requests.post(config.url + '/message/sendlaterdm/v1', json=message_sendlaterdm_input).json()

def standup_start(user, channel, length):
    '''
    helper function for standup_start
    '''
    input = {
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'length': length,
    }
    return requests.post(config.url + 'standup/start/v1',json=input).json()

def standup_send(user, channel, message):
    '''
    helper function for standup_send
    '''
    input = {
        'token': user['token'],
        'channel_id': channel['channel_id'],
        'message': message,
    }
    return requests.post(config.url + 'standup/send/v1',json=input).json()

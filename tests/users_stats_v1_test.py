from datetime import datetime
import requests
import time
from src import config
from src.error import AccessError

'''
users_stats_v1_test,py: All functions related to testing the users_stats_v1 function

the test function:
    test_invalid_user_token()
    test_simple_case(), lt is the test for no channel/dm/message 
    test_general(), more information in the function doc of test_general()
    test_message_sendlater_in_channel_dm_and_standup_send()

helper functions:
    user_stats(user)
    check_users_stats_of_all_users_and_timestamp_for_specific_key(users, keys)
    check_related_num_of_all_key_and_timestamp_for_specific_key(user, keys)
    check_num_of_existing_channels_dms_messages(user)
    check_utilization_rate(return_dict)

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
    claer()
'''

# define global varieable for this module
NUM_USERS = 0
NUM_USERS_IN_CHANNEL_OR_DM = 0
NUM_CHANNELS_EXIST = 0
NUM_DMS_EXIST = 0
NUM_MESSAGES_EXIST = 0
USERS = []


# Test Cases:

def test_invalid_token():
    '''
    test invalid token, this shouldd raise AccessError
    '''
    requests.delete(config.url + 'clear/v1')
    assert requests.get(config.url + 'users/stats/v1', params={'token': 'invalid_token'}).status_code == AccessError.code

def test_no_channel_dm_message():
    '''
    test when num_users_in_channel_or_dm == 0
    then the utilization_rate should be 0
    '''
    # make sure this test is not affected by message_sendlater(dm) and standup_send
    time.sleep(3)
    # clear data_store
    clear()
  
    # register a user
    user_register('0000@unsw.edu.au', 'password', 'firstname0', 'lastname0')

    # compare the result return by users_stats and calculated result
    keys = ['channels_exist', 'dms_exist', 'messages_exist']
    check_users_stats_of_all_users_and_timestamp_for_specific_key(USERS, keys)


def test_simple_case():
    #'''
    #test  involvement is greater than 1 (by deleting messages)
    #involvement_rate will be capped at 1
    #'''
    # clear data_store
    clear()
    global NUM_USERS_IN_CHANNEL_OR_DM

    # register a user
    user0 = user_register('0000@unsw.edu.au', 'password', 'firstname0', 'lastname0')

    # create a channel
    public_0 = channel_create(user0, 'public_0', True)
    NUM_USERS_IN_CHANNEL_OR_DM += 1

    # get the input for helper funvtion users/stats/v1, and check value returned by users_stats
    check_users_stats_of_all_users_and_timestamp_for_specific_key(USERS, keys=['channels_exist'])
    
    # send a message in the channel, check the time_stamp for 'messages_exist'
    message_0 = message_send(user0, public_0, '1')
    check_users_stats_of_all_users_and_timestamp_for_specific_key(USERS, keys=['messages_exist'])


    # send second message in the channel, 
    message_1 = message_send(user0, public_0, '1')
    check_users_stats_of_all_users_and_timestamp_for_specific_key(USERS, keys=['messages_exist'])

    
    # then remove first message
    message_remove(user0, message_0)
    check_users_stats_of_all_users_and_timestamp_for_specific_key(USERS, keys=['messages_exist'])
    
    # remove second message, compare the final result, involvement_rate is capeed to be 1
    message_remove(user0, message_1)
    check_users_stats_of_all_users_and_timestamp_for_specific_key(USERS, keys=['messages_exist'])


    
    # then do the same test to dm
    clear()
    user0 = user_register('0000@unsw.edu.au', 'password', 'firstname0', 'lastname0')
    user1 = user_register('0001@unsw.edu.au', 'password', 'firstname1', 'lastname1')

    # create a dm
    dm_0 = dm_create(user0, [user1])
    NUM_USERS_IN_CHANNEL_OR_DM += 2
    check_users_stats_of_all_users_and_timestamp_for_specific_key(USERS, keys=['dms_exist'])
    
    # send a message in the dm, then remove it
    message_0 = message_senddm(user0, dm_0, '1')
    check_users_stats_of_all_users_and_timestamp_for_specific_key(USERS, keys=['messages_exist'])
    
    #remove this message
    message_remove(user0, message_0)
    check_users_stats_of_all_users_and_timestamp_for_specific_key(USERS, keys=['messages_exist'])

def test_general():
    '''
    This is a large test it show the behaviour of users_stats after the functions below is called: 
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
    clear()
    global NUM_USERS_IN_CHANNEL_OR_DM
    # register user0
    user0 = user_register('0000@unsw.edu.au', 'password', 'firstname0', 'lastname0')

    # create channel public_0
    public_0 = channel_create(user0, 'public_0', True)
    NUM_USERS_IN_CHANNEL_OR_DM += 1
    check_users_stats_of_all_users_and_timestamp_for_specific_key(USERS, keys=['channels_exist'])

    # register public_0_member and invite to channel public_0
    user1 = user_register('0001@unsw.edu.au', 'password', 'firstname1', 'lastname1')
    channel_join(user1, public_0)
    NUM_USERS_IN_CHANNEL_OR_DM += 1
    check_users_stats_of_all_users_and_timestamp_for_specific_key(USERS, keys=[])

    # register private_0_owner and create channel private_0
    user2 = user_register('0002@unsw.edu.au', 'password', 'firstname2', 'lastname2')
    private_0 = channel_create(user2, 'private_0', False)
    NUM_USERS_IN_CHANNEL_OR_DM += 1
    check_users_stats_of_all_users_and_timestamp_for_specific_key(USERS, keys=['channels_exist'])

    # invite user1 to private_0
    channel_invite(user2, private_0, user1)
    check_users_stats_of_all_users_and_timestamp_for_specific_key(USERS, keys=[])

    # test user1 leave the channel 'public_0'
    channel_leave(user1, public_0)
    check_users_stats_of_all_users_and_timestamp_for_specific_key(USERS, keys=[])

    # test user1 rejoin the channel 'public_0' and send two message
    channel_join(user1, public_0)
    print(users_stats(user0))
    print()
    message_0 = message_send(user1, public_0, '0')
    check_users_stats_of_all_users_and_timestamp_for_specific_key(USERS, keys=[])

    message_send(user1, public_0, '1')
    check_users_stats_of_all_users_and_timestamp_for_specific_key(USERS, keys=['messages_exist'])
    
    # test user1 share message0 to private_0
    message_share(user1, message_0, '0', channel_id=private_0['channel_id'], dm_id=-1)
    check_users_stats_of_all_users_and_timestamp_for_specific_key(USERS, keys=['messages_exist'])

    # test user0 send a message in 'public_0'
    message_send(user0, public_0, '2')
    check_users_stats_of_all_users_and_timestamp_for_specific_key(USERS, keys=['messages_exist'])
    
    
    # delete message_0 (the first message sent by user1)
    message_remove(user0, message_0)
    check_users_stats_of_all_users_and_timestamp_for_specific_key(USERS, keys=['messages_exist'])

    
    # now start dm test
    # create a dm including user0 and user2
    dm_0 = dm_create(user0, [user2])
    check_users_stats_of_all_users_and_timestamp_for_specific_key(USERS, keys=['dms_exist'])

    # user2 send a message in the dm, then remove it
    message_0 = message_senddm(user2, dm_0, '0')
    check_users_stats_of_all_users_and_timestamp_for_specific_key(USERS, keys=['messages_exist'])

    # remove this message
    message_remove(user2, message_0)
    check_users_stats_of_all_users_and_timestamp_for_specific_key(USERS, keys=['messages_exist'])

    # user2 leave the dm_0
    dm_leave(user2, dm_0)
    check_users_stats_of_all_users_and_timestamp_for_specific_key(USERS, keys=[])
    
    # remove the dm_0
    dm_remove(user0, dm_0)
    check_users_stats_of_all_users_and_timestamp_for_specific_key(USERS, keys=['dms_exist'])

    # the untested functions now are:
    #   message_sendlater, message_sendlaterdm
    #   standup_start standup_send

def test_message_sendlater_in_channel_dm_and_standup_send():
    '''
    test the left functions: 
        message_sendlater, message_sendlaterdm
        standup_start standup_send
    '''
    # reset data_store and global variables
    clear()
    global NUM_USERS_IN_CHANNEL_OR_DM

    # register two users
    user0 = user_register('0000@unsw.edu.au', 'password', 'firstname0', 'lastname0')
    user1 = user_register('0001@unsw.edu.au', 'password', 'firstname1', 'lastname1')
    check_users_stats_of_all_users_and_timestamp_for_specific_key(USERS, keys=[])

    # create a dm
    dm_0 = dm_create(user0, [user1])
    NUM_USERS_IN_CHANNEL_OR_DM = 2
    check_users_stats_of_all_users_and_timestamp_for_specific_key(USERS, keys=['dms_exist'])

    # test message send later dm
    message_sendlaterdm(user0, dm_0, '0', int(datetime.utcnow().timestamp()) + 1)
    time.sleep(2)
    check_users_stats_of_all_users_and_timestamp_for_specific_key(USERS, keys=['messages_exist'])

    # create channel public_0
    public_0 = channel_create(user0, 'public_0', True)
    check_users_stats_of_all_users_and_timestamp_for_specific_key(USERS, keys=['channels_exist'])

    # join user1 channel public_0
    channel_join(user1, public_0)
    check_users_stats_of_all_users_and_timestamp_for_specific_key(USERS, keys=[])
    
    # test message send later in channel
    message_sendlater(user0, public_0, '1', int(datetime.utcnow().timestamp()) + 1)
    time.sleep(2)
    check_users_stats_of_all_users_and_timestamp_for_specific_key(USERS, keys=['messages_exist'])

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
    check_users_stats_of_all_users_and_timestamp_for_specific_key(USERS, keys=['messages_exist'])

    # waiting the end of standup, check users_stats
    time.sleep(3)
    global NUM_MESSAGES_EXIST
    NUM_MESSAGES_EXIST += 1
    check_users_stats_of_all_users_and_timestamp_for_specific_key(USERS, keys=['messages_exist'])








# Help functions:

def users_stats(user):
    '''
    return user stats
    '''
    return requests.get(config.url + 'users/stats/v1', params={'token': user['token']}).json()


def check_users_stats_of_all_users_and_timestamp_for_specific_key(users, keys):
    '''
    call check_related_num_of_all_key_and_timestamp_for_specific_key for each user
    more information is in the function string of that helper function
    '''
    for user in users:
        check_related_num_of_all_key_and_timestamp_for_specific_key(user, keys)

def check_related_num_of_all_key_and_timestamp_for_specific_key(user, keys):
    '''
    check_all_key_of_users_stats_not_including_timestamp also with the utilization_rate:
        so num_channels_exist, num_dms_exist, num_messages_exist is checked
    then check the time_stamp of specific_key
    '''
    timestamp_now = int(datetime.utcnow().timestamp())
    return_dict = users_stats(user)
    check_num_of_existing_channels_dms_messages(user)
    check_utilization_rate(return_dict)
    for key in keys:
        assert return_dict['workspace_stats'][key][-1]['time_stamp'] - timestamp_now < 2

def check_num_of_existing_channels_dms_messages(user):
    '''
    check_num_of_existing_channels_dms_messages
    by comparing the input and the return value of users_stats
    '''
    return_dict = users_stats(user)
    assert return_dict['workspace_stats']['channels_exist'][-1]['num_channels_exist'] == NUM_CHANNELS_EXIST
    assert return_dict['workspace_stats']['dms_exist'][-1]['num_dms_exist'] == NUM_DMS_EXIST
    assert return_dict['workspace_stats']['messages_exist'][-1]['num_messages_exist'] == NUM_MESSAGES_EXIST

def check_utilization_rate(return_dict):
    '''
    check utilization_rate
    utilization_rate = num_users_who_have_joined_at_least_one_channel_or_dm / num_users
    '''
    
    expected_utilization_rate = NUM_USERS_IN_CHANNEL_OR_DM / NUM_USERS
    assert return_dict['workspace_stats']['utilization_rate'] == expected_utilization_rate

# below is the helper functions for calling the functions in server for test
def user_register(email, password, name_first, name_last):
    '''
    register a user and return {'token': token, 'auth_user_id': u_id}
    '''
    input = {
        'email' : email,
        'password' : password,
        'name_first' : name_first,
        'name_last' : name_last
    }
    
    user = requests.post(config.url + 'auth/register/v2', json=input).json()
    global NUM_USERS
    NUM_USERS += 1
    global USERS
    USERS.append(user)
    return user


def channel_create(creator, name, is_public):
    '''
    create a channel and return {'channel_id': channel_id}
    '''
    input = {
        'token': creator['token'],
        'name': name,
        'is_public': is_public
    }
    global NUM_CHANNELS_EXIST
    NUM_CHANNELS_EXIST += 1
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
    global NUM_DMS_EXIST
    NUM_DMS_EXIST += 1
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
    global NUM_DMS_EXIST
    NUM_DMS_EXIST -= 1
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
    global NUM_MESSAGES_EXIST
    NUM_MESSAGES_EXIST += 1
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
    global NUM_MESSAGES_EXIST
    NUM_MESSAGES_EXIST += 1
    return requests.post(config.url + 'message/senddm/v1', json=input).json()


def message_remove(user, message):
    '''
    remove a message with specified message_id
    '''
    input = {
        'token': user['token'],
        'message_id': message['message_id'],
    }
    global NUM_MESSAGES_EXIST
    NUM_MESSAGES_EXIST -= 1
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
    global NUM_MESSAGES_EXIST
    NUM_MESSAGES_EXIST += 1
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
    global NUM_MESSAGES_EXIST
    NUM_MESSAGES_EXIST += 1
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
    global NUM_MESSAGES_EXIST
    NUM_MESSAGES_EXIST += 1
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

def clear():
    '''
    reset the data_store and global variables
    '''
    requests.delete(config.url + 'clear/v1')
    global NUM_USERS
    global NUM_USERS_IN_CHANNEL_OR_DM
    global NUM_CHANNELS_EXIST
    global NUM_DMS_EXIST
    global NUM_MESSAGES_EXIST
    global USERS

    NUM_USERS = 0
    NUM_USERS_IN_CHANNEL_OR_DM = 0
    NUM_CHANNELS_EXIST = 0
    NUM_DMS_EXIST = 0
    NUM_MESSAGES_EXIST = 0
    USERS = []

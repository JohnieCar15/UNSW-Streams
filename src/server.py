import sys
import signal
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src.error import InputError
from src import config
from src.channel import channel_details_v2, channel_invite_v2, channel_join_v2, channel_messages_v2, channel_leave_v1
from src.auth import auth_register_v2, auth_login_v2, auth_logout_v1
from src.dm import dm_create_v1, dm_list_v1, dm_details_v1
from src.channels import channels_create_v2, channels_list_v2, channels_listall_v2
from src.user import users_all_v1, user_profile_v1
from src.user import user_profile_setname_v1, user_profile_setemail_v1, user_profile_sethandle_v1
from src.other import clear_v1
from src.message import message_send_v1, message_edit_v1, message_remove_v1

from src.admin import admin_userpermission_change_v1

def quit_gracefully(*args):
    '''For coverage'''
    exit(0)
    
def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

#### NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS

@APP.route('/channel/details/v2', methods=['GET'])
def channel_details_endpoint():
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    return dumps(channel_details_v2(token, channel_id))

@APP.route("/channel/messages/v2", methods=['GET'])
def channel_messages_v2_ep():
    token = request.args.get('token')
    channel_id = request.args.get('channel_id')
    start = request.args.get('start')

    return dumps(channel_messages_v2(token, int(channel_id), int(start)))

@APP.route("/dm/details/v1", methods=['GET'])
def dm_details_v1_endpoint():
    token = request.args.get('token')
    dm_id = int(request.args.get('dm_id'))
    return dumps (dm_details_v1(token, dm_id))
    
@APP.route('/channels/create/v2', methods=['POST'])
def channels_create():
    data = request.get_json()
    return dumps(channels_create_v2(data['token'], data['name'], data['is_public']))


@APP.route("/auth/register/v2", methods=['POST'])
def auth_register_v2_ep():
    data = request.get_json()
    return dumps(auth_register_v2(data['email'], data['password'], data['name_first'], data['name_last']))

@APP.route("/auth/login/v2", methods=['POST'])
def auth_login_v2_ep():
    data = request.get_json()
    return dumps(auth_login_v2(data['email'], data['password']))
    
@APP.route("/channel/join/v2", methods=['POST'])
def channel_join_v2_ep():
    data = request.json
    return dumps(channel_join_v2(data['token'], data['channel_id']))

@APP.route("/channel/invite/v2", methods=['POST'])
def channel_invite_v2_ep():
    data = request.json
    return dumps(channel_invite_v2(data['token'], data['channel_id'], data['u_id']))
    
@APP.route("/auth/logout/v1", methods=['POST'])
def auth_logout_v1_ep():
    data = request.get_json()
    return dumps(auth_logout_v1(data['token']))

@APP.route("/dm/list/v1", methods=['GET'])
def dm_list_v1_ep():
    token = request.args.get('token')

    return dumps(dm_list_v1(token))

@APP.route("/dm/create/v1", methods=['POST'])
def dm_create_endpoint():
    data = request.get_json()
    return dumps(dm_create_v1(data['token'], data['u_ids']))

@APP.route("/users/all/v1", methods=['GET'])
def users_all():
    token = request.args.get('token')
    users_profile = users_all_v1(token)
    return dumps(users_profile)

@APP.route("/user/profile/v1", methods=['GET'])
def user_profile():
    token = request.args.get('token')
    u_id = int(request.args.get('u_id'))
    user_profile = user_profile_v1(token, u_id)
    return dumps(user_profile)

@APP.route("/user/profile/setname/v1", methods=['PUT'])
def user_setname():
    data = request.get_json()
    token = data['token']
    name_first = data['name_first']
    name_last = data['name_last']
    user_profile_setname_v1(token, name_first, name_last)
    return dumps({})

@APP.route("/user/profile/setemail/v1", methods=['PUT'])
def user_setemail():
    data = request.get_json()
    token = data['token']
    email = data['email']
    user_profile_setemail_v1(token, email)
    return dumps({})

@APP.route("/user/profile/sethandle/v1", methods=['PUT'])
def user_sethandle():
    data = request.get_json()
    token = data['token']
    handle = data['handle_str']
    user_profile_sethandle_v1(token, handle)
    return dumps({})

@APP.route("/channels/list/v2", methods=['GET'])
def channels_list():
    token = request.args.get('token')
    return dumps(channels_list_v2(token))

@APP.route("/channels/listall/v2", methods=['GET'])
def channels_listall():
    token = request.args.get('token')
    return dumps(channels_listall_v2(token))

@APP.route("/admin/userpermission/change/v1", methods=['POST'])
def admin_userpermission_change_v1_ep():
    data = request.json
    return dumps(admin_userpermission_change_v1(data['token'], data['u_id'], data['permission_id']))

@APP.route("/clear/v1", methods=['DELETE'])
def clear_v1_ep():
    clear_v1()
    return dumps({})

@APP.route("/message/send/v1", methods=['POST'])
def message_send_v1_ep():
    data = request.get_json()

    return dumps(message_send_v1(data['token'], data['channel_id'], data['message']))

@APP.route("/message/edit/v1", methods=['PUT'])
def message_edit_v1_ep():
    data = request.get_json()

    return dumps(message_edit_v1(data['token'], data['message_id'], data['message']))

@APP.route("/message/remove/v1", methods=['DELETE'])
def message_remove_v1_ep():
    data = request.get_json()

    return dumps(message_remove_v1(data['token'], data['message_id']))

@APP.route("/channel/leave/v1", methods=['POST'])
def channel_leave_endpoint():
    data = request.get_json()
    return dumps(channel_leave_v1(data['token'], data['channel_id']))
#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port

import sys
import signal
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src.error import InputError
from src import config
from src.channel import channel_details_v2, channel_invite_v2, channel_join_v2
from src.auth import auth_register_v2, auth_login_v2, auth_logout_v1
from src.channels import channels_create_v2
<<<<<<< HEAD
from src.channel import channel_invite_v2
from src.auth import auth_register_v2
from src.auth import auth_login_v2
from src.channels import channels_list_v2, channels_listall_v2
=======
from src.user import users_all_v1, user_profile_v1
from src.user import user_profile_setname_v1
from src.user import user_profile_setemail_v1
from src.user import user_profile_sethandle_v1

>>>>>>> master
from src.other import clear_v1

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

# Example
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
   	    raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })

@APP.route('/channel/details/v2', methods=['GET'])
def channel_details_endpoint():
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    return dumps(channel_details_v2(token, channel_id))

@APP.route('/channels/create/v2', methods=['POST'])
def channels_create():
    data = request.get_json()
    return dumps(channels_create_v2(data['token'], data['name'], data['is_public']))

@APP.route("/channel/invite/v2", methods=['POST'])
def channel_invite_v2_ep():
    data = request.json
    return dumps(channel_invite_v2(data['token'], data['channel_id'], data['u_id']))

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

@APP.route("/user/users/all/v1", methods=['GET'])
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

@APP.route("/clear/v1", methods=['DELETE'])
def clear():
    clear_v1()
    return dumps({})

<<<<<<< HEAD
@APP.route("/clear/v2", methods=['DELETE'])
def clear2():
    clear_v1()
    return dumps({})
=======
>>>>>>> master
#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port

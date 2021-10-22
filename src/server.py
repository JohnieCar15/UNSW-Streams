import sys
import signal
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src.error import InputError
from src import config
from src.auth import auth_register_v2, auth_login_v2, auth_logout_v1
from src.channels import channels_create_v2
from src.dm import dm_leave_v1
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

@APP.route("/auth/logout/v1", methods=['POST'])
def auth_logout_v1_ep():
    data = request.get_json()

    return dumps(auth_logout_v1(data['token']))

@APP.route("/dm/leave/v1", methods=['POST'])
def dm_leave_v1_ep():
    data = request.get_json()

    return dumps(dm_leave_v1(data['token'], data['dm_id']))

@APP.route("/clear/v1", methods=['DELETE'])
def clear():
    clear_v1()
    return dumps({})
    
#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port

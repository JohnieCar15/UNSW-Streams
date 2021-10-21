import sys
import signal
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src.error import InputError
from src import config
from src.auth import auth_register_v2
from src.auth import auth_login_v2
from src.other import clear_v1
from src.user import user_profile_v1

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

@APP.route("/auth/register/v2", methods=['POST'])
def auth_register_v2_ep():
    data = request.get_json()

    return dumps(auth_register_v2(data['email'], data['password'], data['name_first'], data['name_last']))

@APP.route("/auth/login/v2", methods=['POST'])
def auth_login_v2_ep():
    data = request.get_json()

    return dumps(auth_login_v2(data['email'], data['password']))

@APP.route("/user/profile/v1", methods=['GET'])
def user_profile():
    token = request.args.get('token')
    u_id = int(request.args.get('u_id'))
    user_profile = user_profile_v1(token, u_id)
    print(user_profile)
    return dumps(user_profile)

@APP.route("/clear/v1", methods=['DELETE'])
def clear():
    clear_v1()
    return dumps({})
    
#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port

import pytest
import requests

from src import config
from src.error import InputError
import re
import imaplib
import email
'''
auth_passwordreset_reset_v1_test.py: All functions related to testing the auth_passwordreset_reset_v1 function
'''
@pytest.fixture()
def clear_and_request():
    '''
    Clears the datastore, registers a user, then requests a password reset
    '''
    requests.delete(config.url + '/clear/v1')

    auth_register_input = {
        'email':'t13abeagle@gmail.com',
        'password':'password',
        'name_first':'First',
        'name_last':'Last'
    }

    requests.post(config.url + 'auth/register/v2', json=auth_register_input)

    requests.post(config.url + 'auth/passwordreset/request/v1', json={'email': "t13abeagle@gmail.com"})
    
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login("t13abeagle@gmail.com", "t13abeaglecs1531")
    mail.list()

    mail.select("inbox")

    data = mail.search(None, "ALL")[1]

    latest_email_id = data[0].split()[-1]

    data = mail.fetch(latest_email_id, "(RFC822)")[1]

    raw_email = data[0][1].decode('utf-8')

    msg = email.message_from_string(raw_email)

    reset_code = re.findall('[0-9]+', msg.get_payload(decode=True).decode('utf-8'))[0]

    return reset_code

def test_auth_passwordreset_reset_v1(clear_and_request):
    '''
    Tests if valid reset_code changes password of user
    '''
    reset_code = clear_and_request

    requests.post(config.url + 'auth/passwordreset/reset/v1', json={'reset_code': reset_code, 'new_password': 'thisisatest'})

    auth_login_input = {
        'email':'t13abeagle@gmail.com',
        'password':'thisisatest'
    }

    login_return = requests.post(config.url + 'auth/login/v2', json=auth_login_input)

    assert login_return.status_code == 200

def test_invalid_reset_code():
    '''
    Tests if invalid reset_code raises error
    '''
    requests.delete(config.url + '/clear/v1')

    reset_return = requests.post(config.url + 'auth/passwordreset/reset/v1', json={'reset_code': '-1', 'new_password': 'aaaaaa'})

    assert reset_return.status_code == InputError.code

def test_short_password(clear_and_request):
    '''
    Tests if short passworrd raises error
    '''
    reset_code = clear_and_request

    reset_return = requests.post(config.url + 'auth/passwordreset/reset/v1', json={'reset_code': reset_code, 'new_password': 'a'})

    assert reset_return.status_code == InputError.code

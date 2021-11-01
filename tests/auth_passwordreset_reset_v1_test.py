import pytest
import requests

from src import config
from src.error import InputError

def test_invalid_reset_code():
    requests.delete(config.url + '/clear/v1')

    reset_return = requests.post(config.url + 'auth/passwordreset/request/v1', json={'reset_code': None, 'new_password': 'aaaaaa'})

    assert reset_return.status_code == InputError.code

def test_short_password():
    requests.delete(config.url + '/clear/v1')

    reset_return = requests.post(config.url + 'auth/passwordreset/request/v1', json={'reset_code': None, 'new_password': 'a'})

    assert reset_return.status_code == InputError.code

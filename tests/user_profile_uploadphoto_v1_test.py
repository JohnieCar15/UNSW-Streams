import pytest
import requests

from src import config
from src.error import InputError, AccessError

@pytest.fixture
def clear_and_register():
    requests.delete(config.url + 'clear/v1')
    register = requests.post(config.url + 'auth/register/v2', json={'email': 'yes@yes.com', 'password': 'aaaaaa', 'name_first': "firstname", "name_last": "lastname"})
    register_data = register.json()
    
    return register_data['token']

def test_user_profile_uploadphoto_v1(clear_and_register):
    token = clear_and_register

    uploadphoto_input = {
        'token': token, 
        'img_url': 'http://www.ll-mm.com/images/placeholders/masonry3-placeholder.jpg', 
        'x_start': 0, 
        'y_start': 0, 
        'x_end': 1, 
        'y_end': 1
    }

    uploadphoto_return = requests.post(config.url + 'user/profile/uploadphoto/v1', json=uploadphoto_input)

    assert uploadphoto_return.status_code == 200

def test_invalid_token():
    requests.delete(config.url + 'clear/v1')

    uploadphoto_input = {
        'token': None, 
        'img_url': 'http://www.ll-mm.com/images/placeholders/masonry3-placeholder.jpg', 
        'x_start': 0, 
        'y_start': 0, 
        'x_end': 1, 
        'y_end': 1
    }

    uploadphoto_return = requests.post(config.url + 'user/profile/uploadphoto/v1', json=uploadphoto_input)

    assert uploadphoto_return.status_code == AccessError.code
'''
def test_invalid_img_url(clear_and_register):
    token = clear_and_register

    uploadphoto_input = {
        'token': token, 
        'img_url': "http://www.ll-mm.com/images/placeholders/masonry3-placeholder-asdasdasd.jpg", 
        'x_start': 0, 
        'y_start': 0, 
        'x_end': 1, 
        'y_end': 1
    }

    uploadphoto_return = requests.post(config.url + 'user/profile/uploadphoto/v1', json=uploadphoto_input)

    assert uploadphoto_return.status_code == InputError.code
'''
def test_invalid_x_start(clear_and_register):
    token = clear_and_register

    uploadphoto_input = {
        'token': token, 
        'img_url': 'http://www.ll-mm.com/images/placeholders/masonry3-placeholder.jpg', 
        'x_start': -1, 
        'y_start': 0, 
        'x_end': 1, 
        'y_end': 1
    }

    uploadphoto_return = requests.post(config.url + 'user/profile/uploadphoto/v1', json=uploadphoto_input)

    assert uploadphoto_return.status_code == InputError.code

def test_invalid_y_start(clear_and_register):
    token = clear_and_register

    uploadphoto_input = {
        'token': token, 
        'img_url': 'http://www.ll-mm.com/images/placeholders/masonry3-placeholder.jpg', 
        'x_start': 0, 
        'y_start': -1, 
        'x_end': 1, 
        'y_end': 1
    }

    uploadphoto_return = requests.post(config.url + 'user/profile/uploadphoto/v1', json=uploadphoto_input)

    assert uploadphoto_return.status_code == InputError.code

def test_invalid_x_end(clear_and_register):
    token = clear_and_register

    uploadphoto_input = {
        'token': token, 
        'img_url': 'http://www.ll-mm.com/images/placeholders/masonry3-placeholder.jpg', 
        'x_start': 0, 
        'y_start': 0, 
        'x_end': 300, 
        'y_end': 1
    }

    uploadphoto_return = requests.post(config.url + 'user/profile/uploadphoto/v1', json=uploadphoto_input)

    assert uploadphoto_return.status_code == InputError.code

def test_invalid_y_end(clear_and_register):
    token = clear_and_register

    uploadphoto_input = {
        'token': token, 
        'img_url': 'http://www.ll-mm.com/images/placeholders/masonry3-placeholder.jpg', 
        'x_start': 0, 
        'y_start': 0, 
        'x_end': 1, 
        'y_end': 300
    }

    uploadphoto_return = requests.post(config.url + 'user/profile/uploadphoto/v1', json=uploadphoto_input)

    assert uploadphoto_return.status_code == InputError.code

def test_x_end_less_than_x_start(clear_and_register):
    token = clear_and_register

    uploadphoto_input = {
        'token': token, 
        'img_url': 'http://www.ll-mm.com/images/placeholders/masonry3-placeholder.jpg', 
        'x_start': 2, 
        'y_start': 0, 
        'x_end': 1, 
        'y_end': 1
    }

    uploadphoto_return = requests.post(config.url + 'user/profile/uploadphoto/v1', json=uploadphoto_input)

    assert uploadphoto_return.status_code == InputError.code

def test_y_end_less_than_y_start(clear_and_register):
    token = clear_and_register

    uploadphoto_input = {
        'token': token, 
        'img_url': 'http://www.ll-mm.com/images/placeholders/masonry3-placeholder.jpg', 
        'x_start': 0, 
        'y_start': 2, 
        'x_end': 1, 
        'y_end': 1
    }

    uploadphoto_return = requests.post(config.url + 'user/profile/uploadphoto/v1', json=uploadphoto_input)

    assert uploadphoto_return.status_code == InputError.code

def test_img_not_jpg(clear_and_register):
    token = clear_and_register

    uploadphoto_input = {
        'token': token, 
        'img_url': 'http://www.ll-mm.com/images/placeholders/iphone5-placeholder.png', 
        'x_start': 0, 
        'y_start': 0, 
        'x_end': 1, 
        'y_end': 1
    }

    uploadphoto_return = requests.post(config.url + 'user/profile/uploadphoto/v1', json=uploadphoto_input)

    assert uploadphoto_return.status_code == InputError.code

import pytest
import requests

from src import config
from src.error import InputError, AccessError
'''
user_profile_uploadphoto_v1_test.py: All functions related to testing the user_profile_uploadphoto_v1 function
'''
@pytest.fixture
def clear_and_register():
    '''
    Clears datastore then registers a user
    '''
    requests.delete(config.url + 'clear/v1')
    register = requests.post(config.url + 'auth/register/v2', json={'email': 'yes@yes.com', 'password': 'aaaaaa', 'name_first': "firstname", "name_last": "lastname"})
    register_data = register.json()
    
    return register_data['token']

def test_user_profile_uploadphoto_v1(clear_and_register):
    '''
    Tests if valid input gives correct output
    '''
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
    '''
    Tests if invalid token raises error
    '''
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

def test_invalid_img_url(clear_and_register):
    '''
    Tests if invalid img_url raises error
    '''
    token = clear_and_register

    uploadphoto_input = {
        'token': token, 
        'img_url': "asdkajsflkanf.jpg", 
        'x_start': 0, 
        'y_start': 0, 
        'x_end': 1, 
        'y_end': 1
    }

    uploadphoto_return = requests.post(config.url + 'user/profile/uploadphoto/v1', json=uploadphoto_input)

    assert uploadphoto_return.status_code == InputError.code

def test_https_img_url(clear_and_register):
    '''
    Tests if https img_url works with function
    '''
    token = clear_and_register

    uploadphoto_input = {
        'token': token, 
        'img_url': "https://tinyjpg.com/images/social/website.jpg", 
        'x_start': 0, 
        'y_start': 0, 
        'x_end': 1000, 
        'y_end': 500
    }

    uploadphoto_return = requests.post(config.url + 'user/profile/uploadphoto/v1', json=uploadphoto_input)

    assert uploadphoto_return.status_code == 200

def test_invalid_x_start(clear_and_register):
    '''
    Tests if invalid x_start raises error
    '''
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
    '''
    Tests if invalid y_start raises error
    '''
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
    '''
    Tests if invalid x_end raises error
    '''
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
    '''
    Tests if invalid y_end raises error
    '''
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
    '''
    Tests if invalid x crop raises error
    '''
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
    '''
    Tests if invalid y crop raises error
    '''
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
    '''
    Tests if none jpg image raises error
    '''
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

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
    Clearing datastore and registering user
    '''
    requests.delete(config.url + 'clear/v1')
    register = requests.post(config.url + 'auth/register/v2', json={'email': 'yes@yes.com', 'password': 'aaaaaa', 'name_first': "firstname", "name_last": "lastname"})
    register_data = register.json()
    
    return register_data['token']

def test_user_profile_uploadphoto_v1(clear_and_register):
    '''
    Successful case of uploading and cropping a photo
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
    Error case of passing an invalid token
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
    Error case of an invalid image url
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
    Testing case of https img url
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
    Error case of invalid x start coordinate
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
    Error case of invalid y start coordinate
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
    Error case of invalid x end coordinate
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
    Error case of invalid y end coordinate
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
    Error case of invalid x start and end coordinates
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
    Error case of invalid y start and end coordinates
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
    Error case of non jpg image
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

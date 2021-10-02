import pytest

from src.other import clear_v1
from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.error import InputError
from src.error import AccessError


@pytest.fixture
def clear_and_register():
    clear_v1()
    id = auth_register_v1("z0000000@gmail.com" , "aaaaaa", "firstname", "lastname" )
    return id['auth_user_id']


def test_valid_id_valid_name_public(clear_and_register):
    id_return = clear_and_register
    assert channels_create_v1(id_return, 'name', True) == {'channel_id': 1}

def test_valid_id_valid_name_private(clear_and_register):
    id_return = clear_and_register
    assert channels_create_v1(id_return, 'name', False) == {'channel_id': 1}

def test_valid_id_invalid_name_public(clear_and_register):
    id_return = clear_and_register
    with pytest.raises(InputError):
        channels_create_v1(id_return,'' , True) 

def test_valid_id_invalid_name_private(clear_and_register):
    id_return = clear_and_register
    with pytest.raises(InputError):
        channels_create_v1(id_return,'' , False)

def test_valid_id_invalid_name_2_public(clear_and_register):
    id_return = clear_and_register
    with pytest.raises(InputError):
        channels_create_v1(id_return,'aaaaaaaaaaaaaaaaaaaaa' , True) 

def test_valid_id_invalid_name_2_private(clear_and_register):
    id_return = clear_and_register
    with pytest.raises(InputError):
        channels_create_v1(id_return,'aaaaaaaaaaaaaaaaaaaaa' , False) 

def test_invalid_id_invalid_name_public():
    clear_v1()
    id = -1
    with pytest.raises(AccessError):
        channels_create_v1(id, "", True)

def test_invalid_id_invalid_name_private():
    clear_v1()
    id = -1
    with pytest.raises(AccessError):
        channels_create_v1(id, "", False)

def test_invalid_id_invalid_name_2_public():
    clear_v1()
    id = -1
    with pytest.raises(AccessError):
        channels_create_v1(id, "aaaaaaaaaaaaaaaaaaaaa", True)

def test_invalid_id_invalid_name_2_private():
    clear_v1()
    id = -1
    with pytest.raises(AccessError):
        channels_create_v1(id, "aaaaaaaaaaaaaaaaaaaaa", False)

def test_invalid_id_valid_name_public():
    clear_v1()
    id = -1
    with pytest.raises(AccessError):
        channels_create_v1(id, "name", True)

def test_invalid_id_valid_name_private():
    clear_v1()
    id = -1
    with pytest.raises(AccessError):
        channels_create_v1(id, "name", False)
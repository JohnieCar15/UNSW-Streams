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

# change later for implementation
def test_valid_id_valid_name_public(clear_and_register):
    assert channels_create_v1(id, 'name', True) == {'channel_id': 1}
    
def test_valid_id_invalid_name(clear_and_register):
    with pytest.raises(InputError):
        assert channels_create_v1(id,'' , True) 

def test_valid_id_invalid_name_2(clear_and_register):
    with pytest.raises(InputError):
        assert channels_create_v1(id,'aaaaaaaaaaaaaaaaaaaaa' , True) 

def test_invalid_id_invalid_name():
    clear_v1()
    id = -1
    with pytest.raises(AccessError):
        assert channels_create_v1(id, "", True)


def test_invalid_id_valid_name():
    clear_v1()
    id = -1
    with pytest.raises(AccessError):
        assert channels_create_v1(id, "name", True)


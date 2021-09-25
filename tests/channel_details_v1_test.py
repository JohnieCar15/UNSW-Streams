import pytest

from src.other import clear_v1
from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.error import InputError
from src.error import AccessError

def test_valid_channel_authorised():
    clear_v1()
    id_num = auth_register_v1("yes@yes.com", "aaaaaa", "firstname", "lastname")
    channel_id = channels_create_v1( id_numb, "name", True )
    assert channel_details_v1( id_num, channel_id) == {
        'name': 'aaaaaa',
        'owner_members': [
            {
                'u_id': id_num,
                'email': 'yes@yes.com',
                'name_first': 'firstname',
                'name_last': 'lastname',
                'handle_str': 'firstnamelastname',
            }
        ],
        'all_members': [
            {
                'u_id': id_num,
                'email': 'yes@yes.com',
                'name_first': 'firstname',
                'name_last': 'lastname',
                'handle_str': 'firstnamelastname',
            }
        ],
    }
    
def test_valid_channel_unauthorised():
    clear_v1()
    id_num = auth_register_v1("yes@yes.com", "aaaaaa", "firstname", "lastname")
    id_num_2 = auth_register_v1("yes2@yes.com" , "aaaaaa", "firstname", "lastname")
    channel_id = channels_create_v1(id_num, "name", True )
    with pytest.raises(AccessError):
        assert channel_details_v1( id_num_2, channel_id)

def test_valid_channel_invalid_id():
    clear_v1()
    id_num = auth_register_v1("yes@yes.com", "aaaaaa", "firstname", "lastname")
    channel_id = channels_create_v1(id_num, "name", True )
    with pytest.raises(AccessError):
        assert channel_details_v1( (id_num + 1), channel_id)


def test_invalid_channel_unauthorised():
    clear_v1()
    id_num = auth_register_v1("yes@yes.com", "aaaaaa", "firstname", "lastname")
    with pytest.raises(AccessError):
        assert channel_details_v1 ( id_num, 1)

def test_invalid_channel_invalid_id():
    clear_v1()
    with pytest.raises(AccessError):
        assert channel_details_v1(1, 1)
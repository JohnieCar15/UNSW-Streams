import pytest

from src.other import clear_v1
from src.auth import auth_register_v1
from src.channels import channels_create_v1
from src.channel import channel_details_v1, channel_invite_v1
from src.error import InputError, AccessError

# When clear_v1() is run, the data store is empty so all ids passed will be invalid

@pytest.fixture
def clear_and_register():
    clear_v1()
    id_return = auth_register_v1("yes@yes.com", "aaaaaa", "firstname", "lastname")
    return id_return['auth_user_id']

# testing when the channel id is valid and called by an authorised member
def test_valid_channel_authorised(clear_and_register):
    id_num = clear_and_register
    channel_id_ret = channels_create_v1(id_num, "name", True )
    channel_id = channel_id_ret['channel_id']

    assert channel_details_v1( id_num, channel_id) == {
        'name': 'name',
        'is_public': True,
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

# testing when the channel id is valid and has two members when called by an authorised member
def test_valid_channel_2_members(clear_and_register):
    id_num = clear_and_register
    id_num_2_return = auth_register_v1("yes2@yes.com", "aaaaaa", "name", "name")
    id_num_2 = id_num_2_return['auth_user_id']
    channel_id_ret = channels_create_v1(id_num, "name", True)
    channel_id = channel_id_ret['channel_id']
    channel_invite_v1(id_num, channel_id, id_num_2)

    assert channel_details_v1( id_num, channel_id) == {
        'name': 'name',
        'is_public': True,
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
            } ,

            {
                'u_id': id_num_2,
                'email': 'yes2@yes.com',
                'name_first': 'name',
                'name_last': 'name',
                'handle_str': 'namename',
            }
        ],
    }
    
 # testing valid channel called by user who isn't a member
def test_valid_channel_unauthorised(clear_and_register):
    id_num = clear_and_register
    id_num_2_ret = auth_register_v1("yes2@yes.com" , "aaaaaa", "firstname", "lastname")
    id_num_2 = id_num_2_ret['auth_user_id']
    channel_id_ret = channels_create_v1(id_num, "name", True )
    channel_id = channel_id_ret['channel_id']

    with pytest.raises(AccessError):
        channel_details_v1(id_num_2, channel_id)

# testing valid channel called by an invalid user id
def test_valid_channel_invalid_id(clear_and_register):
    
    id_num = clear_and_register
    channel_id_ret = channels_create_v1(id_num, "name", True )
    channel_id = channel_id_ret['channel_id']

    with pytest.raises(AccessError):
        assert channel_details_v1(id_num + 1, channel_id)

# testing invalid channel id
def test_invalid_channel_unauthorised(clear_and_register): 
    id_num = clear_and_register
    with pytest.raises(InputError):
        assert channel_details_v1 (id_num, 1)

# testing invalid channel id called by an invalid user id
def test_invalid_channel_invalid_id():
    clear_v1()
    with pytest.raises(AccessError):
        assert channel_details_v1(1, 1)

# testing invalid channel id called by a valid user id
def test_invalid_channel_id_valid_id(clear_and_register):
    id_num = clear_and_register
    channel_id_ret = channels_create_v1(id_num, "name", True )
    channel_id = channel_id_ret['channel_id']

    with pytest.raises(InputError):
        assert channel_details_v1(id_num, channel_id + 1)


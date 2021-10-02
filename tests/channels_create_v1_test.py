import pytest

from src.other import clear_v1
from src.auth import auth_register_v1
from src.channels import channels_create_v1, channels_list_v1
from src.error import InputError, AccessError

# When clear_v1() is run, the data store is empty so all ids passed will be invalid

@pytest.fixture
def clear_and_register():
    clear_v1()
    id = auth_register_v1("z0000000@gmail.com" , "aaaaaa", "firstname", "lastname" )
    return id['auth_user_id']

# Test valid auth id with valid name for public channel
def test_valid_id_valid_name_public(clear_and_register):
    id_return = clear_and_register
    channels_create_id = channels_create_v1(id_return, 'name', True)['channel_id']
    channels_list_id = channels_list_v1(id_return)['channels'][0]['channel_id']
    assert channels_create_id == channels_list_id
    
# Test valid auth id with valid name for private channel
def test_valid_id_valid_name_private(clear_and_register):
    id_return = clear_and_register
    channels_create_id = channels_create_v1(id_return, 'name', False)['channel_id']
    channels_list_id = channels_list_v1(id_return)['channels'][0]['channel_id']
    assert channels_create_id == channels_list_id

# Test valid auth id with invalid short name for public channel 
def test_valid_id_invalid_short_channel_name_public(clear_and_register):
    id_return = clear_and_register
    with pytest.raises(InputError):
        channels_create_v1(id_return,'' , True) 

# Test valid auth id with invalid short name for private channel
def test_valid_id_invalid_short_channel_name_private(clear_and_register):
    id_return = clear_and_register
    with pytest.raises(InputError):
        channels_create_v1(id_return,'' , False)

# Test valid auth id with invalid long name for public channel
def test_valid_id_invalid_long_channel_name_public(clear_and_register):
    id_return = clear_and_register
    with pytest.raises(InputError):
        channels_create_v1(id_return,'aaaaaaaaaaaaaaaaaaaaa' , True) 

# Test valid auth id with invalid long name for private channel
def test_valid_id_invalid_long_channel_name_private(clear_and_register):
    id_return = clear_and_register
    with pytest.raises(InputError):
        channels_create_v1(id_return,'aaaaaaaaaaaaaaaaaaaaa' , False) 

# Test invalid auth id with invalid short name for public channel 
def test_invalid_id_invalid_short_channel_name_public():
    clear_v1()
    id = -1
    with pytest.raises(AccessError):
        channels_create_v1(id, "", True)

# Test invalid auth id with invalid short name for private channel
def test_invalid_id_invalid_short_channel_name_private():
    clear_v1()
    id = -1
    with pytest.raises(AccessError):
        channels_create_v1(id, "", False)

# Test invalid auth id with invalid long name for public channel 
def test_invalid_id_invalid_long_channel_name_public():
    clear_v1()
    id = -1
    with pytest.raises(AccessError):
        channels_create_v1(id, "aaaaaaaaaaaaaaaaaaaaa", True)

# Test invalid auth id with invalid long name for private channel 
def test_invalid_id_invalid_long_channel_name_private():
    clear_v1()
    id = -1
    with pytest.raises(AccessError):
        channels_create_v1(id, "aaaaaaaaaaaaaaaaaaaaa", False)

# Test invalid auth id with valid name for public channel
def test_invalid_id_valid_name_public():
    clear_v1()
    id = -1
    with pytest.raises(AccessError):
        channels_create_v1(id, "name", True)

# Test invalid auth id with valid name for private channel 
def test_invalid_id_valid_name_private():
    clear_v1()
    id = -1
    with pytest.raises(AccessError):
        channels_create_v1(id, "name", False)
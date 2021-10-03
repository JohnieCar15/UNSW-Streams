## Assumptions for project-backend


* With auth_register_v1, if a user's first name and last name are all non-alphanumeric characters, an InputError will be raised.
* With auth_register_v1, if a new user is created with name_first='first' and name_last='last0' and a handle of 'firstlast0' already exists, then the new handle should be 'firstlast00' not 'firstlast1'.
* With channel_details_v1, if a valid auth_user_id and an invalid channel_id is passed in, an InputError will be returned, despite the fact than an invalid channel_id implies that no user is a member of that channel, which would return an AccessError.
* With channels_list_v1, the order of the returned list of channels is not important and that any tests written will succeed for any order of the correct list.
* With channel_messages_v1, a negative start value is invalid in channel_messages_v1 and an InputError will be raised.
* After clear_v1 is run, the datastore will be completely empty and have no users or channels, hence any value passed in for user_id or channel_id into a function will automatically be invalid.
* All inputs passed into the functions will be of the correct data type and format.

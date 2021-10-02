h1 Assumptions for project_backend

---


* Assume that if a user's first name and last name are all non-alphanumeric characters, an InputError is raised
* Assume that if a channel id is invalid then no user can be a member of that channel 
* Assume that if a handle firstlast0 exists and someone inputs name_first: 'first', name_last: 'last0' the handle should be firstlast00 not firstlast1 
* Assume channels_list_v1 will return {list of channels} in the form of  {'channels': [{'channel_id': channel_id, 'name': 'channel_name'}, ... ]} and according to the [ed forum post](https://edstem.org/au/courses/7025/discussion/613604) the order of those channels is not important, so the test will be passed for any order of the correct list
* Assume that negative start values are invalid in channel_messages_v1 and an error must be raised
* Assume that after clear_v1() the initial state will have no users or channels so any user or channel ids passed into a function will be invalid 

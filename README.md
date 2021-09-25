# COMP1531 Major Project

**✨ Teamwork makes the [UNSW] Streams work 🌈**

## Contents

  1.  Aims
  2.  Overview
  3.  Iteration 1: Basic functionality and tests
  4.  Iteration 2
  5.  Iteration 3
  6.  Interface specifications
  7.  Due Dates and Weightings
  8.  Other Expectations
  9.  Automarking
  10. Plagiarism

## 0. Change Log

* 24/09: Edited channel membership `AccessError`s to require a valid `channel_id`, clarified handle generation instructions, removed references to DMs in permissions section
* 25/09: Clarified `channel_join_v1`'s `AccessError`

## 1. Aims:

* To provide students with hands on experience testing, developing, and maintaining a backend server in Python.
* To develop students' problem solving skills in relation to the software development lifecycle.
* Learn to work effectively as part of a team by managing your project, planning, and allocation of responsibilities among the members of your team.
* Gain experience in collaborating through the use of a source control and other associated modern team-based tools.
* Apply appropriate design practices and methodologies in the development of their solution
* Develop an appreciation for product design and an intuition of how a typical customer will use a product.

## 2. Overview

<b>Please watch our introduction video here</b>:
 * [Part 1: About the project](https://youtu.be/iARiNetEZV8)
 * [Part 2: Getting started](https://youtu.be/_nlrxuYTdIc)

To manage the transition from trimesters to hexamesters in 2021, UNSW has established a new focus on building an in-house digital collaboration and communication tool for groups and teams to support the high intensity learning environment.

Rather than re-invent the wheel, UNSW has decided that it finds the functionality of **<a href="https://www.microsoft.com/en-au/microsoft-teams/group-chat-software">Microsoft Teams</a>** to be nearly exactly what it needs. For this reason, UNSW has contracted out Penguin Pty Ltd (a small software business run by Hayden) to build the new product. In UNSW's attempt to try and add a lighter note to the generally fatigued and cynical student body, they have named their UNSW-based product **UNSW Streams** (or just **Streams** for short). **UNSW Streams** is the communication tool that allows you to share, communication, and collaborate to (attempt to) make streams a reality.

Penguin Pty Ltd has sub-contracted two software firms:

* BlueBottle Pty Ltd (two software developers, Andrea and Andrew, who will build the initial web-based GUI)
* YourTeam Pty Ltd (a team of talented misfits completing COMP1531 in 21T3), who will build the backend Python server

In summary, UNSW contracts Penguin Pty Ltd, who sub contracts:

* BlueBottle (Andrea and Andrew) for frontend work
* YourTeam (you and others) for backend work

Penguin Pty Ltd met with Andrea and Andrew (the frontend development team) 2 weeks ago to brief them on this project. While you are still trying to get up to speed on the requirements of this project, Andrea and Andrew understand the requirements of the project very well.

Because of this they have already specified a **common interface** for the frontend and backend to operate on. This allows both parties to go off and do their own development and testing under the assumption that both parties will comply with the common interface. This is the interface **you are required to use**.

The specific capabilities that need to be built for this project are described in the interface at the bottom. This is clearly a lot of features, but not all of them are to be implemented at once.

## 3. Iteration 1: Basic Functionality and Tests

### 3.1. Task

In this iteration, you are expected to:

1. Write tests for and implement the basic functionality of Streams. The basic functionality is defined as the `auth_*`, `channel_*`, `channels_*` capabilities/functions, as per the interface section below.
    * Test files you add should all be in the form `*_test.py`.
    * Do NOT attempt to try and write or start a web server. Don't overthink how these functions are meant to connect to a frontend yet. That is for the next iteration. In this iteration you are just focusing on the basic backend functionality.

2. Write down any assumptions that you feel you are making in your interpretation of the specification.
    * The `assumptions.md` file described above should be in the root of your repository. If you've not written markdown before (which we assume most of you haven't), it's not necessary to research the format. Markdown is essentially plain text with a few extra features for basic formatting. You can just stick with plain text if you find that easier.
    * We will only be marking the quality of six of your assumptions. You can indicate which you would like marked, otherwise we will look at the first six.

3. Follow best practices for git, project management, and effective teamwork, as discussed in lectures.
    * The marking will be heavily biased toward how well you follow good practices and work together as a team. Just having a "working" solution at the end is not, on its own, sufficient to even get a passing mark.

    * You need to use the **GitLab Issue Boards** for your task tracking and allocation. Don't do it in a Google doc or some other method - your tutor will not award marks for this. Spend some time getting to know how to use the taskboard.

    * You are expected to meet regularly with your group, and document the meetings in meeting minutes which should be stored at a timestamped location in your repo (e.g. uploading a word doc/pdf or writing in the GitLab repo Wiki after each meeting).

    * You should have regular standups and be able to demonstrate evidence of this to your tutor.

    * For this iteration you will need to collectively make a minimum of **12** merge requests into `master`.

### 3.2. Implementing and testing features

You should first approach this project by considering its distinct "features". Each feature should add some meaningful functionality to the project, but still be as small as possible. You should aim to size features as the smallest amount of functionality that adds value without making the project more unstable. For each feature you should:

1. Create a new branch.
2. Write tests for that feature and commit them to the branch. These will fail as you have not yet implemented the feature.
3. Implement that feature.
4. Make any changes to the tests such that they pass with the given implementation. You should not have to do a lot here. If you find that you are, you're not spending enough time on your tests.
5. Consider any assumptions you made in the previous steps and add them to `assumptions.md`.
6. Commit your work and create a merge request for the branch.
7. Get someone in your team who **did not** work on the feature to review the merge request.
8. Fix any issues identified in the review.
9. Merge the merge request into master.

For this project, a feature is typically sized somewhere between a single function, and a whole file of functions (e.g. `auth.py`). It is up to you and your team to decide what each feature is.

There is no requirement that each feature be implemented by only one person. In fact, we encourage you to work together closely on features, especially to help those who may still be coming to grips with Python.

Please pay careful attention to the following:

* We want to see **evidence that you wrote your tests before writing the implementation**. As noted above, the commits containing your initial tests should appear *before* your implementation for every feature branch. If we don't see this evidence, we will assume you did not write your tests first and your mark will be reduced.
* Merging in merge requests with failing pipelines is **very bad practice**. Not only does this interfere with your team's ability to work on different features at the same time, and thus slow down development, it is something you will be penalised for in marking.
* Similarly, merging in branches with untested features is also **very bad practice**. We will assume, and you should too, that any code without tests does not work.
* Pushing directly to `master` is not possible for this repo. The only way to get code into master is via a merge request. If you discover you have a bug in `master` that got through testing, create a bugfix branch and merge that in via a merge request.
* As is the case with any system or functionality, there will be some things that you can test extensively, some things that you can test sparsely/fleetingly, and some things that you can't meaningfully test at all. You should aim to test as extensively as you can, and make judgements as to what things fall into what categories.

### 3.3. File structure and stub code

The tests you write should be as small and independent as possible. This makes it easier to identify why a particular test may be failing. Similarly, try to make it clear what each test is testing for. Meaningful test names and documentation help with this. An example of how to structure tests has been done in:

* `src/echo.py`
* `tests/echo_test.py`

The echo functionality is tested, both for correct behaviour and for failing behaviour. As echo is relatively simple functionality, only 2 tests are required. For the larger features, you will need many tests to account for many different behaviours.

To allow you to import Python code from a directory with the same syntax as you would a module, the directory must be turned into a Python package. More information can be found <a href="https://docs.python.org/3.7/tutorial/modules.html#packages">here</a>. We have already done this for you with the `src/` and `tests/` directories, by
creating two files:
  * `src/__init__.py`
  * `tests/__init__.py`

A number of files have been added to your `src/` directory in your repository. These files are:
 * `auth.py`
 * `channel.py`
 * `channels.py`
 * `other.py`

They do not contain any real implementation, but do contain some stub code to show you the structure of what the different functions should return. You will replace these stubs with actual implementations as you develop.

#### 3.3.1. Authentication

Elements of securely storing passwords and other tricky authorisation methods are not required for iteration 1. You can simply store passwords plainly, and the user ID is used to identify them. We will discuss ways to improve the quality and methods of these capabilities in iteration 2.

As a reminder, the `auth_user_id` variable is the user ID of the user who is making the request. If you imagine a user logs into your site who has user ID `12`, when they make subsequent calls to functions the user ID of the person calling it is passed in as the `auth_user_id` variable.

### 3.4 Test writing guidelines

To test basic functionality you will likely need code like:

```python
result = auth.auth_register('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
auth.auth_login('validemail@gmail.com', '123abc!@#') # Expect to work since we registered
```

and

```python
result = auth.auth_register('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
with pytest.raises(InputError):
    auth.auth_login('didntusethis@gmail.com', '123abcd!@#') # Expect fail since we never registered
```

However, when deciding how to structure your tests, keep in mind the following:

* Your tests should be *black box* unit tests.
  * Black box means they should not depend your specific implementation, but rather work with *any* working implementation. You should design your tests such that if they were run against another group's backend they would still pass.
  * Unit tests mean the tests focus on testing particular functions, rather than the system as a whole. Certain unit tests will depend on other tests succeeding. It's OK to write tests that are only a valid test if other functions are correct (e.g. to test `channel` functions you can assume that `auth` is implemented correctly).

* Avoid writing your tests such that they need to be run in a particular order. That can make it hard to identify what exactly is failing.

* You should reset the state of the application (e.g. deleting all users, channels, messages, etc.) at the start of every test. That way you know none of them are accidentally dependent on an earlier test. You can use a function for this that is run at the beginning of each test (hint: `clear_v1`).

* If you find yourself needing similar code at the start of a series of tests, consider using a **fixture** to avoid repetition.

### 3.5. Storing data

Nearly all of the functions will likely have to reference some "data source" to store information. E.G. If you register two users, create two channels, and then add a user to a channel, all of that information needs to be "stored" somewhere. The most important thing for iteration 1 is not to overthink this problem.

Firstly, you do **not have to use an SQL database, or something like firebase**.

Secondly, you don't need to make anything persist. What that means is that if you run all your pytests, and then run them again later, the data is OK to be "fresh" every time you run `pytest`. We will cover persistence in another iteration.

Inside `src/data_store.py` we have provided you with a custom class called `Datastore` which stores a data structure that contains information that you will need to access across multiple functions. There is a variable called `data_store` which is a `Datastore` that has been marked as `global`. An explanation of how to use `data_store` is in `data_store.py`. The object stories a dictionary which you will need to determine the internal structure of. If you wish, you are allowed to modify this class.

For example, you could define a structure in a file that is empty, and as functions are called it populates and fills up like the one below:

```python
data = {
    'users': [
        {
            'id': 1,
            'name' : 'user1',
        },
        {
            'id': 2,
            'name' : 'user2',
        },
    ],
    'channels': [
        {
            'id': 1,
            'name' : 'channel1',
        },
        {
            'id': 2,
            'name' : 'channel2',
        },
    ],
}
```

### 3.6. Dryrun

We have provided a very simple dryrun for iteration 1 consisting of 4 tests, one each for your implementation of `clear_v1`, `auth_register_v1`, `channels_create_v1`, and `channels_list_v1`. These only check the format of your return types, so do not rely on these as an indicator for the correctness of your implementation or tests.

To run the dryrun, you should be in the root directory of your project (e.g. `/project-backend`) and use the command:

```bash
1531 dryrun 1
```

### 3.7. Bad Assumptions

Here are a few examples of bad assumptions:

* Assume that all groups store their data in a field called data which is located in data.py
* Assume all individual return values are returned as single values rather than being stored in a dictionary
* Assume the functions are written correctly
* Assume the input auth_user_id is valid

Bad assumptions are usually ones that directly contradict an explicit or implicit requirement in the specification. Good assumptions are ones that fill holes or gaps in requirements.

### 3.8. Working in parallel

This iteration provides challenges for many groups when it comes to working in parallel. Your group's initial reaction will be that you need to complete registration before you can complete login, and then login must be done before channel creation, etc.

There are several approaches that you can consider to overcome these challenges:

* Have people working on down-stream tasks (like the channels implementation) work with _stubbed_ versions of the up-stream tasks. E.G. The login function is stubbed to return a successful dummy response, and therefore two people can work in parallel.
* Co-ordinate with your team to ensure prerequisite features are completed first (e.g. Emily completes `auth_register` on Monday meaning Nick can start `channels_create` on Tuesday)
* You can pull any other remote branch into your own using the command `git pull origin <branch_name>`.
    * This can be helpful when two people are working on functions on seperate branches where one is a prerequisite of the other and an implementations is required to keep the pipeline passing
    * You should should pull from `master` on a regular basis to ensure your code remains up-to-date

### 3.9. Marking Criteria

<table>
  <tr>
    <th>Section</th>
    <th>Weighting</th>
    <th>Criteria</th>
  </tr>
  <tr>
    <td>Automarking (Testing & Implementation)</td>
    <td>40%</td>
    <td><ul>
      <li>Correct implementation of specified functions</li>
      <li>Correctly written tests based on the specification requirements</li>
    </ul></td>
  </tr>
  <tr>
    <td>Code Quality</td>
    <td>25%</td>
    <td><ul>
      <li>Demonstrated an understanding of good test <b>coverage</b></li>
      <li>Demonstrated an understanding of the importance of <b>clarity</b> on the communication test and code purposes</li>
      <li>Demonstrated an understanding of thoughtful test <b>design</b></li>
      <li>Appropriate use of Python data structures (lists, dictionaries, etc.)</li>
      <li>Appropriate style as described in section 8.4
    </ul></td>
  </tr>
  <tr>
    <td>Git Practices</td>
    <td>15%</td>
    <td><ul>
      <li>Meaningful and informative git commit names being used</li>
      <li>Effective use of merge requests (from branches being made) across the team (as covered in lectures)</li>
      <li>At least 12 merge requests into master made</li>
    </ul></td>
  </tr>
  <tr>
    <td>Project Management & Teamwork</td>
    <td>15%</td>
    <td><ul>
      <li>A generally equal contribution between team members</li>
      <li>Clear evidence of reflection on group's performance and state of the team, with initiative to improve in future iterations</li>
      <li>Effective use of course-provided MS Teams for communicating, demonstrating an ability to communicate and manage effectivelly digitally</li>
      <li>Use of issue board on Gitlab to track and manage tasks</li>
      <li>Effective use of agile methods such as standups</li>
      <li>Minutes/notes taken from group meetings (and stored in a logical place in the repo)</li>
    </ul></td>
  </tr>
  <tr>
    <td>Assumptions markdown file</td>
    <td>5%</td>
    <td><ul>
      <li>Clear and obvious effort and time gone into thinking about possible assumptions that are being made when interpreting the specification</li>
    </ul></td>
  </tr>
</table>

For this and for all future milestones, you should consider the other expectations as outlined in section 8 below.

The formula used for automarking in this iteration is:

`Mark = t * i` (Mark equals `t` multiplied by `i`)

Where:
 * `t` is the mark you receive for your tests running against your code (100% = your implementation passes all of your tests)
 * `i` is the mark you receive for our course tests (hidden) running against your code (100% = your implementation passes all of our tests)

### 3.10. Submission

This iteration due date and demonstration week is described in section 7. You will demonstrate this submission in line with the information provided in section 7.

## 4. Iteration 2

Coming Soon

## 5. Iteration 3

Coming Soon

## 6. Interface specifications

These interface specifications come from Andrea and Andrew, who are building the frontend to the requirements set out below.

### 6.1. Input/Output types

<table>
  <tr>
    <th>Variable name</th>
    <th>Type</th>
  </tr>
  <tr>
    <td>named exactly <b>email</b></td>
    <td>string</td>
  </tr>
  <tr>
    <td>has suffix <b>id</b></td>
    <td>integer</td>
  </tr>
  <tr>
    <td>named exactly <b>length</b></td>
    <td>integer</td>
  </tr>
  <tr>
    <td>contains substring <b>password</b></td>
    <td>string</td>
  </tr>
  <tr>
    <td>named exactly <b>message</b></td>
    <td>string</td>
  </tr>
  <tr>
    <td>contains substring <b>name</b></td>
    <td>string</td>
  </tr>
  <tr>
    <td>has prefix <b>is_</b></td>
    <td>boolean</td>
  </tr>
  <tr>
    <td>has prefix <b>time_</b></td>
    <td>integer (unix timestamp), [check this out](https://www.tutorialspoint.com/How-to-convert-Python-date-to-Unix-timestamp)</td>
  </tr>
  <tr>
    <td>(outputs only) named exactly <b>messages</b></td>
    <td>List of dictionaries, where each dictionary contains types { message_id, u_id, message, time_created }</td>
  </tr>
  <tr>
    <td>(outputs only) named exactly <b>channels</b></td>
    <td>List of dictionaries, where each dictionary contains types { channel_id, name }</td>
  </tr>
  <tr>
    <td>has suffix <b>_str</b></td>
    <td>string</td>
  </tr>
  <tr>
    <td>(outputs only) name ends in <b>members</b></td>
    <td>List of dictionaries, where each dictionary contains types of <b>user</b></td>
  </tr>
  <tr>
    <td>(outputs only) named exactly <b>user</b></td>
    <td>Dictionary containing u_id, email, name_first, name_last, handle_str</td>
  </tr>
  <tr>
    <td>(outputs only) named exactly <b>users</b></td>
    <td>List of dictionaries, where each dictionary contains types of <b>user</b></td>
  </tr>
</table>

### 6.2. Interface

<table>
  <tr>
    <th>Name & Description</th>
    <th style="width:18%">Data Types</th>
    <th style="width:32%">Exceptions</th>
  </tr>
  <tr>
    <td><code>auth_login_v1</code><br /><br />Given a registered user's email and password, returns their `auth_user_id` value.</td>
    <td><b>Parameters:</b><br /><code>{ email, password }</code><br /><br /><b>Return Type:</b><br /><code>{ auth_user_id }</code></td>
    <td>
      <b>InputError</b> when any of:
      <ul>
        <li>email entered does not belong to a user</li>
        <li>password is not correct</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>auth_register_v1</code><br /><br />Given a user's first and last name, email address, and password, create a new account for them and return a new `auth_user_id`.<br /><br />A handle is generated that is the concatenation of their casted-to-lowercase alphanumeric (a-z0-9) first name and last name (i.e. make lowercase then remove non-alphanumeric characters). If the concatenation is longer than 20 characters, it is cut off at 20 characters. Once you've concatenated it, if the handle is once again taken, append the concatenated names with the smallest number (starting from 0) that forms a new handle that isn't already taken. The addition of this final number may result in the handle exceeding the 20 character limit (the handle 'abcdefghijklmnopqrst0' is allowed if the handle 'abcdefghijklmnopqrst' is already taken).</td>
    <td><b>Parameters:</b><br /><code>{ email, password, name_first, name_last }</code><br /><br /><b>Return Type:</b><br /><code>{ auth_user_id }</code></td>
    <td>
      <b>InputError</b> when any of:
      <ul>
        <li>email entered is not a valid email (more in section 6.4)</li>
        <li>email address is already being used by another user</li>
        <li>length of password is less than 6 characters</li>
        <li>length of name_first is not between 1 and 50 characters inclusive</li>
        <li>length of name_last is not between 1 and 50 characters inclusive</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>channels_create_v1</code><br /><br />Creates a new channel with the given name that is either a public or private channel. The user who created it automatically joins the channel. For this iteration, the only channel owner is the user who created the channel.</td>
    <td><b>Parameters:</b><br /><code>{ auth_user_id, name, is_public }</code><br /><br /><b>Return Type:</b><br /><code>{ channel_id }</code></td>
    <td>
      <b>InputError</b> when:
      <ul>
        <li>length of name is less than 1 or more than 20 characters</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>channels_list_v1</code><br /><br />Provide a list of all channels (and their associated details) that the authorised user is part of.</td>
    <td><b>Parameters:</b><br /><code>{ auth_user_id }</code><br /><br /><b>Return Type:</b><br /><code>{ channels }</code></td>
    <td>N/A</td>
  </tr>
  <tr>
    <td><code>channels_listall_v1</code><br /><br />Provide a list of all channels, including private channels, (and their associated details)</td>
    <td><b>Parameters:</b><br /><code>{ auth_user_id }</code><br /><br /><b>Return Type:</b><br /><code>{ channels }</code></td>
    <td>N/A</td>
  </tr>
  <tr>
    <td><code>channel_details_v1</code><br /><br />Given a channel with ID channel_id that the authorised user is a member of, provide basic details about the channel.</td>
    <td><b>Parameters:</b><br /><code>{ auth_user_id, channel_id }</code><br /><br /><b>Return Type:</b><br /><code>{ name, is_public, owner_members, all_members }</code></td>
    <td>
      <b>InputError</b> when:
      <ul>
        <li>channel_id does not refer to a valid channel</li>
      </ul>
      <b>AccessError</b> when:
      <ul>
        <li>channel_id is valid and the authorised user is not a member of the channel</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>channel_join_v1</code><br /><br />Given a channel_id of a channel that the authorised user can join, adds them to that channel.</td>
    <td><b>Parameters:</b><br /><code>{ auth_user_id, channel_id }</code><br /><br /><b>Return Type:</b><br /><code>{}</code></td>
    <td>
      <b>InputError</b> when any of:
      <ul>
        <li>channel_id does not refer to a valid channel</li>
        <li>the authorised user is already a member of the channel</li>
      </ul>
      <b>AccessError</b> when:
      <ul>
        <li>channel_id refers to a channel that is private and the authorised user is not already a channel member and is not a global owner</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>channel_invite_v1</code><br /><br />Invites a user with ID u_id to join a channel with ID channel_id. Once invited, the user is added to the channel immediately. In both public and private channels, all members are able to invite users.</td>
    <td><b>Parameters:</b><br /><code>{ auth_user_id, channel_id, u_id }</code><br /><br /><b>Return Type:</b><br /><code>{}</code></td>
    <td>
      <b>InputError</b> when any of:
      <ul>
        <li>channel_id does not refer to a valid channel</li>
        <li>u_id does not refer to a valid user</li>
        <li>u_id refers to a user who is already a member of the channel</li>
      </ul>
      <b>AccessError</b> when:
      <ul>
        <li>channel_id is valid and the authorised user is not a member of the channel</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>channel_messages_v1</code><br /><br />Given a channel with ID channel_id that the authorised user is a member of, return up to 50 messages between index "start" and "start + 50". Message with index 0 is the most recent message in the channel. This function returns a new index "end" which is the value of "start + 50", or, if this function has returned the least recent messages in the channel, returns -1 in "end" to indicate there are no more messages to load after this return.</td>
    <td><b>Parameters:</b><br /><code>{ auth_user_id, channel_id, start }</code><br /><br /><b>Return Type:</b><br /><code>{ messages, start, end }</code></td>
    <td>
      <b>InputError</b> when any of:
      <ul>
        <li>channel_id does not refer to a valid channel</li>
        <li>start is greater than the total number of messages in the channel</li>
      </ul>
      <b>AccessError</b> when:
      <ul>
        <li>channel_id is valid and the authorised user is not a member of the channel</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>clear_v1</code><br /><br />Resets the internal data of the application to its initial state</td>
    <td><b>Parameters:</b><br /><code>{  }</code><br /><br /><b>Return Type:</b><br /><code>{}</code></td>
    <td>N/A</td>
  </tr>
</table>


### 6.3. Errors for all functions

Either an `InputError` or `AccessError` is thrown when something goes wrong. All of these cases are listed in the **Interface** table. If input implies that both errors should be thrown, throw an `AccessError`.

One exception is that, even though it's not listed in the table, for all functions except `auth/register`, `auth/login`, `auth/passwordreset/request` (iteration 3) and `auth/passwordreset/reset` (iteration 3), an `AccessError` is thrown when the auth_user_id passed in is not a valid id.

### 6.4. Valid email format

A valid email should match the following regular expression:

```
'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
```

The Python `re` (regular expression) module allows you to determine whether a string matches a regular expression. You do not need to understand regular expressions to effectively utilise the `re` module to check if the email is correct. Check [this link](https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/) if you need more help.

### 6.5. Testing

A common question asked throughout the project is usually "How can I test this?" or "Can I test this?" In any situation, most things can be tested thoroughly. However, some things can only be tested sparsely, and in some other rare occasions, some things can't be tested at all. A challenge of this project is for you to use your discretion to figure out what to test, and how much to test.

### 6.6. Pagination

The behaviour in which channel_messages returns data is called **pagination**. It's a commonly used method when it comes to getting theoretially unbounded amounts of data from a server to display on a page in chunks. Most of the timelines you know and love - Facebook, Instagram, LinkedIn - do this.

For example, in iteration 1, if we imagine a user with `auth_user_id` "12345" is trying to read messages from channel with ID 6, and this channel has 124 messages in it, 3 calls from the client to the server would be made. These calls, and their corresponding return values would be:
 * `channel_messages("12345", 6, 0) => { [messages], 0, 50 }`
 * `channel_messages("12345", 6, 50) => { [messages], 50, 100 }`
 * `channel_messages("12345", 6, 100) => { [messages], 100, -1 }`

### 6.7. Permissions

 * Members in a channel have one of two channel permissions
   1) Owner of the channel (the person who created it, and whoever else that creator adds)
   2) Members of the channel
 * Streams users have two global permissions
   1) Owners (permission id 1), who can also modify other owners' permissions
   2) Members (permission id 2), who do not have any special permissions
* All Streams users are members by default, except for the very first user who signs up, who is an owner

A user's primary permissions are their global permissions. Then the channel permissions are layered on top. For example:
* An owner of Streams has channel owner permissions in every channel they've joined. Despite obtaining owner permissions upon joining a channel, they do not become channel owners unless a channel owner adds them as one, meaning if they are removed as a global owner, they will no longer have those channel owner permissions.
* A member of Streams is a member in channels they are not owners of
* A member of Streams is an owner in channels they are owners of

## 7. Due Dates and Weightings

|Iteration|Due date                              |Demonstration to tutor(s)      |Assessment weighting of project (%)|
|---------|--------------------------------------|-------------------------------|-----------------------------------|
|   1     |10am Monday 4th October (**week 4**)    |In YOUR **week 4** laboratory  |25%                                |
|   2     |10am Monday 25th October (**week 7**)   |In YOUR **week 7** laboratory  |40%                                |
|   3     |10am Monday 15th November (**week 10**) |In YOUR **week 10** laboratory |35%                                |

### 7.1. Submission & Late Penalties

There is no late penalty, as we do not accept late submissions. You will be assessed on the most recent version of your work at the due date and time listed.

To submit your work, open up a CSE terminal and run:

` $ 1531 submit [iteration] [groupname]`

For example:

` $ 1531 submit iteration1 W11A_EAGLE`

This will submit a copy of your latest git commit to our systems for automarking. Your tutor will also request you pull up this copy when marking you in the demonstration.

If the deadline is approaching and you have features that are either untested or failing their tests, **DO NOT MERGE IN THOSE MERGE REQUESTS**. In some cases, your tutor will look at unmerged branches and may allocate some reduced marks for incomplete functionality, but `master` should only contain working code.

### 7.2. Demonstration

For the demonstrations in weeks 4, 7, and 10, all team members **must** attend this lab session, or they will not receive a mark.

When you demonstrate this iteration in your lab time, it will consist of a 15 minute Q&A in front of your tutor and maybe some other students in your tutorial. For online classes, webcams are required to be on during this Q&A (your phone is a good alternative if your laptop/desktop doesn't have a webcam).

## 8. Other Expectations

While it is up to you as a team to decide how work is distributed between you, for the purpose of assessment there are certain key criteria all members must follow.

* Code contribution
* Documentation contribution
* Usage of git/GitLab
* Attendance
* Peer assessment
* Academic conduct

The details of each of these is below.

While, in general, all team members will receive the same mark (a sum of the marks for each iteration), **if you as an individual fail to meet these criteria your final project mark may be scaled down**, most likely quite significantly.

### 8.1. Project check-in

During your lab class, in weeks without project demonstrations, you and your team will conduct a short stand-up in the presence of your tutor. Each member of the team will briefly state what they have done in the past week, what they intend to do over the next week, and what issues they faced or are currently facing. This is so your tutor, who is acting as a representative of the client, is kept informed of your progress. They will make note of your presence and may ask you to elaborate on the work you've done.

Project check-ins are also excellent opportunities for your tutor to provide you with both technical and non-technical guidance.

### 8.2. Code Style and Documentation

You are required to ensure that your code:
 * Follows Pythonic principles discussed in lectures and tutorials
 * Follows stylistic convenctions discussed in lectures and tutorials
 * (For iterations 2 & 3) your code should achieve a `10.00/10` `pylint` score

Examples of things to focus on include:
* Correct casing of variable, function and class names
* Meaningful variable and function names
* Readability of code and use of whitespace
* Modularisation and use of helper functions where needed

Your functions such as `auth_register`, `channel_invite`, `message_send`, etc. are also required to contain docstrings of the following format:

```
<Brief description of what the function does>

Arguments:
    <name> (<data type>)    - <description>
    <name> (<data type>)    - <description>
    ...

Exceptions:
    InputError  - Occurs when ...
    AccessError - Occurs when ...

Return Value:
    Returns <return value> on <condition>
    Returns <return value> on <condition>
```

In each iteration you will be assessed on ensuring that every relevant function/endpoint in the specification is appropriately documented.

### 8.3. Individual Marks

Whilst we do award a tentative mark to your group as a whole, your actual mark for each iteration is given to you individually. Your individual mark is determined by your tutor, with your group mark as a reference point. Your tutor will look at your code contribution, documentation contribution (for iteration 3), peer assessment results, any other issues raised by group members throughout term, and your attendance at project check-ins and demonstrations.

### 8.3.1. Code contribution

All team members must contribute code to the project to a generally similar degree. Tutors will assess the degree to which you have contributed by looking at your **git history** and analysing lines of code, number of commits, timing of commits, etc. If you contribute significantly less code than your team members, your work will be closely examined to determine what scaling needs to be applied.

### 8.3.2. Documentation contribution

All team members must contribute documentation to the project to a generally similar degree. Tutors will assess the degree to which you have contributed by looking at your **git history** but also **asking questions** (essentially interviewing you) during your demonstration.

Note that, **contributing more documentation is not a substitute for not contributing code**.

### 8.3.3. Peer Assessment

At the end of each iteration there will be a peer assessment survey where you will rate and leave comments about each team member's contribution to the project up until that point. 

Your other team members will **not** be able to see how you rated them or what comments you left in either peer assessment. If your team members give you a less than satisfactory rating, your contribution will be scrutinised and you may find your final mark scaled down.

### 8.3.4. Attendance

It is generally assumed that all team members will be present at the demonstrations and at weekly check-ins. If you're absent for more than 80% of the weekly check-ins or any of the demonstrations, your mark may be scaled down.

If, due to exceptional circumstances, you are unable to attend your lab for a demonstration, please apply for special consideration.

## 9. Automarking

Each iteration consists of an automarking component. The particular formula used to calculate this mark is specific to the iteration (and detailed above).

When running your code or tests as part of the automarking, we place a 2 minutes timer on the running of your groups tests and implementation. This is more than enough time to complete everything unless you're doing something very wrong or silly with your code.

Once you receive your results for each iteration, your mark may be lower than expected. If you find this is due to many marks being lost due to one or two trivial, systematic bugs, you are welcome to branch off the submission commit, make some changes, and push to another branch. If you share this branch with your tutor and ask them to rerun it, they can rerun it for you. Your new automarking mark will be your new mark with a 20% penalty (of the total automark mark) for the change.

In the 5 days preceding each iterations due date (i.e. the Wed, Thu, Fri, Sat, Sun night prior to submission), we will be running your code against the actual automarkers (the same ones that determine your final mark) and publishing the results of every group on a leaderboard. [The leaderboard will be available here once released](http://cgi.cse.unsw.edu.au/~cs1531/21T3/leaderboard). Your position and mark on the leaderboard will be referenced against an alias for your group (for privacy). This alias will be emailed to your group in week 3. You are welcome to share your alias with others if you choose! (Up to you).

The leaderboard gives you a chance to sanity check your automark (without knowing the details of what you did right and wrong), and is just a bit of fun.

## 10. Plagiarism

The work you and your group submit must be your own work. Submission of work partially or completely derived from any other person or jointly written with any other person is not permitted. The penalties for such an offence may include negative marks, automatic failure of the course and possibly other academic discipline. Assignment submissions will be examined both automatically and manually for such submissions.

Relevant scholarship authorities will be informed if students holding scholarships are involved in an incident of plagiarism or other misconduct.

Do not provide or show your project work to any other person, except for your group and the teaching staff of COMP1531. If you knowingly provide or show your assignment work to another person for any reason, and work derived from it is submitted you may be penalized, even if the work was submitted without your knowledge or consent. This may apply even if your work is submitted by a third party unknown to you.

Note, you will not be penalized if your work has the potential to be taken without your consent or knowledge.

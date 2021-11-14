## 1. Description of extra feature
The 'user_status' extra feature mimics the status functionality present in many online social services such as Microsoft Teams. This feature allows Streams users to have their activity status set to reflect their current availability (i.e. 'available', 'busy', 'be right back', 'do not disturb', 'offline') to other Streams users.

## 2. Interface specifications


### 2.1. Input/Output types

<table>
  <tr>
    <th>Variable name</th>
    <th>Type</th>
  </tr>
  <tr>
    <td>named exactly <b>token</b></td>
    <td>string</td>
  </tr>
  <tr>
    <td>named exactly <b>u_ids</b></td>
    <td>List of user ids</td>
  </tr>
  <tr>
    <td>named exactly <b>user_status</b></td>
    <td>string
    </td>
  </tr>
</table>


### 2.2. Interface


<table>
  <tr>
    <th>Name & Description</th>
    <th>HTTP Method</th>
    <th style="width:18%">Data Types</th>
    <th style="width:32%">Exceptions</th>
  </tr>
  <tr>
    <td><code>user/status/v1</code><br /><br />Get the user_status of user with one's u_id.</td>
    <td style="font-weight: bold; color: blue;">GET</td>
    <td><b>Parameters:</b><br /><code>{ token, u_id }</code><br /><br /><b>Return Type:</b><br /><code>{ user_status }</code></td>
    <td>
      <b>InputError</b> when:
      <ul>
        <li>u_id does not refer to a valid user</li>
      </ul>
      </ul>
    </td>
  </tr>
  <tr>
    <td><code>user/setstatus/v1</code><br /><br />Set the user_status of user.</td>
    <td style="font-weight: bold; color: blue;">PUT</td>
    <td><b>Parameters:</b><br /><code>{ token, user_status }</code><br /><br /><b>Return Type:</b><br /><code>{ }</code></td>
    <td>
      <b>InputError</b> when:
      <ul>
        <li>'user_status' is not valid status string</li>
      </ul>
      </ul>
    </td>
  </tr>
</table>

### 2.3. Errors for all functions

Either an `InputError` or `AccessError` is thrown when something goes wrong. All of these cases are listed in the **Interface** table. If input implies that both errors should be thrown, throw an `AccessError`.


### 2.4. Details of user_status
Any Streams user can set their user status at any time. In certain cases, a user's status will be automatically set to the following values:
* Set to 'available':
    * when a user has registered or logged in
    * after the user has finished all standups, except the user set status during the standup he/her attended.
* Set to 'away':
    * after an hour (now set to 5 seconds for testing on CSE machine) of the user's last action, excluding cases when the user's status is set to 'offline' or 'busy'.
* Set to 'busy':
    * after a user joins an active standup (by starting a standup or send a message in an active standup).
* Set to 'offline':
    * after the user logs out of all active sessions.

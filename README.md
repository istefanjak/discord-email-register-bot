# Discord Email Register Bot
###### Name: Eliminator
###### Author: istefanjak


## Main features:
1. Ability to make channel access private by sending verification tokens via email
1. One user per one email account
1. Methods of controlling emails:
	1. Regex pattern
	2. Blacklist
	
## Installation:
*Tested on Python 3.7*

**Requirements:**
* MySQL server
* SMTP server

```
pip install --upgrade pip
pip install discord.py
pip install aiomysql
pip install aiosmtplib
```
**First Time setup:**
* Edit /constants.py
* Suggested to edit /cogs/dm/dev.py for custom messages inside commands

**Discord Server setup:**
* Make sure you give the bot right permissions for sending messages, viewing channels and managing roles
* Make sure you pull the bot role to the top of the role hierarchy inside server settings -> roles (IMPORTANT!)
* Make sure you created all the necessary roles, defined in /constants.py

**MySQL Server setup:**
* Edit /asyncdb.py and use #util tagged functions inside run() method for the first time setup. Individually run the module.

## How does it function?
List of commands (all commands are given over DM communication with the bot):
* `register <role> <email>` ->  registers the user with given `email`. User has to choose one of the roles defined in `constants.py`, `REGISTERED_ROLE_NAMES`. The email first goes through the regex pattern check defined in the same file and also the blacklist check.
* `validate <token>` -> used after `register`. If successful, the bot gives user the role sent in previous step.
* `deregister` -> used for deregistering a successfully validated user.

Bot admin commands:
* ```blacklist add <email(s)>``` -> add one or multiple emails to blacklist
* ```blacklist remove <email(s)>``` -> remove one or multiple emails from the blacklist
* ```blacklist get``` -> get the blacklist and print it
* ```postasbot <msg>``` -> post msg as bot, to the channel defined in `constants.py`, `BOT_CHANNEL`
* ```postasbotdesc``` -> post as bot, message defined in the function body inside `/cogs/dm/dev.py`

## Dependency links:
* [discord.py](https://github.com/Rapptz/discord.py)
* [aiomysql](https://github.com/aio-libs/aiomysql)
* [aiosmtplib](https://github.com/cole/aiosmtplib)
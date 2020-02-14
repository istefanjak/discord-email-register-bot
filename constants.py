#Regex for a valid acceptable email format
EMAIL_REGEX = r"^([a-zA-Z0-9]{3,})@gmail\.com$"

#DISCORD VARIABLES
#
#Discord ID for admin user, it is used in bot server messages where a problem arises
#and contact for help is being sent.
#Format <@ID>, e.g. <@123456789>
#Discord ID of a user can easily be obtained by enabling the setting inside Discord GUI
# -> Settings -> Appearance -> Advanced -> Developer mode
#Now right clicking on a username option "Copy ID" is shown.
ADMIN_USER = ""

#Access token for Discord app
TOKEN = ""

#Channel name which is being used for dev commands postasbot and postasbotdesc and where
#the messages appear. (CASE SENSITIVE!)
BOT_CHANNEL = "register-channel"

#Command prefix
BOT_COMMAND_PREFIX = "$"

#Server ID, of INT type, obtained the same way as described for ADMIN_USER, right clicking
#on a server and clicking Copy ID
SERVERID = 0

#List of valid role names which the bot can assign to the user after a successful validation.
#Needs to be at least 1 role inside the list (CASE SENSITIVE!)
REGISTERED_ROLE_NAMES = ["Registered1", "Registered2"]

#List of roles used for bot administration. (CASE SENSITIVE!)
#Enables these users to use dev COG commands.
DEVELOPER_ROLE_NAMES = ["Developer", "Admin"]

#Bot description
BOT_DESC = "Eliminator bot"

#Discord styling of code blocks in bot messages
CODE_STYLE = "fix"


#MYSQL SERVER VARIABLES
#
#Self-explanatory, PORT of type INT
HOST = ""
PORT = 0
USER = ""
PASS = ""
DB_NAME = ""
#Main table name, where the generated tokens are saved
TABLE_NAME = "token_table"
#Blacklist table name
BLACKLIST_TABLE_NAME = "blacklist_table"


#SMTP SERVER VARIABLES
#
#Self-explanatory, PORT of type INT
SMTP_HOST = ""
SMTP_PORT = 0
SMTP_USER = ""
SMTP_PASS = ""
#Format of email message, SMTP_BODY must contain sequence {token} which is where
#the token will be pasted
SMTP_SENT_FROM = ""
SMTP_SUBJECT = ""
SMTP_BODY = "Your access token is:\r\n\r\n{token}"

#LOG FILE
#
#Custom log file in project's root directory
LOG_FILE = "bot.log"
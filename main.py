"""
# author = Cornelius Prinsloo 
# contact = codedoes@gmail.com


# Instructions for use
- Create your own app at: https://discordapp.com/developers/applications/me
- Set the app as a bot
- Click on the "click to reveal" for the bot's Token
- Copy the entire value and paste it below in token

- visit the following url, changing the client_id to your apps client_id 
    https://discordapp.com/api/oauth2/authorize?client_id=290680806110789633&scope=bot&permissions=0x10000000
- Add the bot to your server

- In discord, go into user settings, 
- click on the "appearance" tab.
- check "developer mode"
- click "done"
- right click on your server icon.
- click "copy ID"
- paste the ID as a string into server_id value below

## Welcome message
- to refer to a channel:
    - go into your server
    - right click on the channel name and select "copy ID"
    - use the format <#channel_id> to refer to the server 
- to refer to a user:
    - go into your server
    - right click on the user and select "copy ID"
    - use the format <@user_id> to refer to the server 

## Granting Roles
- only roles that are lower than the bots top_role can be granted to others
- the bot needs to have `manage roles` permission in one of its roles


## Responding
- If you change the commands.on_message.channel to point to where the message was sent from, you have to make sure that it can respond to wherever you send him a command from. Or else it might have unexpected behaviour.


### Using the bot
## commands
`assign role`
## set up
to give the bot roles it can assign, assign it the roles


"""


import constant
import settings
import commands 

constant.client.run(settings.token)
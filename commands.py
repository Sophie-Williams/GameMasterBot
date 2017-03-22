import discord
from discord.client import Client
from discord.member import Member
from discord.role import Role
from discord.message import Message
from discord.server import Server

from collections import defaultdict
from imp import reload
import constant
import settings;reload(settings)
import messages;reload(messages)


from functools import partial
client = constant.client
server = constant.server

@client.event
async def on_ready():
    global server
    print(' ⌛ checking...')
    server = client.get_server(settings.server_id)
    constant.server=server
    if server is None:
        print(" ✘ settings.server_id is invalid (the bot has not joined this server)")
        await client.close()
    elif not server.me.server_permissions.manage_roles:
        print(" ✘ please assign this bot a role which has the `manage roles` permission")
        await client.close()
    else:
        print(' → is a member of server matching settings.server_id')
        print(' → has `manage roles` permission')
        if server.me.top_role!=server.default_role:
            print(' → has non-default role')
        else:
            print(' ✘ has only default role')
        print(' ✔ ready')
        await client.send_message(server.owner,'\✔ ready')
        
def get_available_roles():
    """
    returns all of the roles below the bot's top_role
    """ 
    top_role = server.me.top_role
    roles = []
    for role in sorted(server.roles):
        if role in server.me.roles and role is not server.me.top_role:
            roles.append(role)
    
    return roles[1:]

async def send_help_message(member:Member):
    message = "__***Commands***__"
    #TODO owner commands (reload)
    message += "\n`hello` - resends the welcome message"
    message += "\n`help` - shows this help message"
    message += "\n`instructions`"
    message += "\n`about studio`"
    message += "\n`about projects`"
#     message += "\n`faq` - shows the frequently asked questions"   
    message += "\n`toc` - shows the terms and conditions"    
    message += "\n`assign role` - type just `assign` to see what roles are available"
    message += "\n`unassign role` - type just `unassign` to see what roles are available"
    if server.me.server_permissions.manage_roles:
        assigns = []
        unassigns = []
        roles = get_available_roles()
#         roles_valid_chart=defaultdict(lambda:False)
#         roles_valid_chart.update(persistance.read()[persistance.rv])
#         permit_member_chart=defaultdict(lambda:False)
#         permit_member_chart.update(persistance.read()[persistance.pm])
        if len(roles)>0:
            message+="\n__***ASSIGNMENT***__"
            for role in reversed(roles):
#                 if roles_valid_chart[role.id]:
                    if role in member.roles:
                        message+="\n`unassign {}`".format(role)
                    else:
                        message+="\n`assign {}`".format(role)
        else:
            message+="\n`no roles available`"
    if member==server.owner:
        message+="\n__***OWNER COMMANDS***__"
        message+='\n`reload` - reloads the scripts'
        message+='\n`greet member_name` - greets a member'
    message+='\n'
    await client.send_message(member,message)
    
signups = []
async def send_welcome_message(member:Member):
    async def enquire_name():
        while True:
            query = await client.send_message(member,"``` ```type in your real name")
            
            name = await client.wait_for_message(channel = query.channel, author = member)
            print([name.channel,name.server,name.author])
            message = await client.send_message(member,"your name is {}".format(name.content))
            await client.add_reaction(message, "✅")
            await client.add_reaction(message, "❎")
            await client.edit_message(message,message.content+"\nIs this correct?")
            while True:
                reaction = (await client.wait_for_reaction(message=message)).reaction
                print(reaction)
                if reaction.emoji=="✅":
                    return name
                elif reaction.emoji=="❎":
                    break
    async def enquire_email():
        while True:
            query = await client.send_message(member,"``` ```type in your email address you want to use")
            email = await client.wait_for_message(channel = query.channel, author = member)
            print([email.channel,email.server,email.author])
            message = (await client.send_message(member,"your email is {}".format(email.content)))
            await client.add_reaction(message, "✅")
            await client.add_reaction(message, "❎")
            await client.edit_message(message,message.content+"\nIs this correct?")
            while True:
                reaction = (await client.wait_for_reaction(message=message)).reaction
                if reaction.emoji=="✅":
                    return email
                elif reaction.emoji=="❎":
                    break
    await client.send_message(member, messages.welcome_message)
#     await send_help_message(member)
    message = await client.send_message(member, messages.instruction)
    await client.add_reaction(message, "✅")
    
    message = await client.edit_message(message, message.content+"\n\nplease click on the ✅ when you have completed the actions")
    await client.wait_for_reaction("✅",user=member,message=message)
    if member not in signups:
        signups.append(member)
        name = await enquire_name()
        try:
            client.change_nickname(member, name.content)
        except discord.Forbidden:
            pass
            
        email = await enquire_email()
        
        while True:
            request = await client.send_message(
                member,
                "``` ```assign yourself a role"
                +"\n{}\n\n`confirm` to submit your details".format(
                    "\n".join("`assign {}`".format(role)
                              for role in get_available_roles() 
                              if role not in member.roles)))
            response = await client.wait_for_message(author=member,channel=request.channel)
            if response.content == "confirm":
                content = "<@{0}>```\n\nname: {1}\nemail: {2}\nroles: {3}```".format(
                    member.id,
                    name.content,
                    email.content,
                    ", ".join(role.name for role in member.roles[1:]))
                print(content)
                await client.send_message(
                    client.get_channel(settings.signup_channel_id),
                    content 
                    )
                await client.send_message(
                    member,
                    content 
                    )
                break
        signups.remove(member)


@client.event
async def on_member_join(member:Member):
    await send_welcome_message(member)




@client.event
async def on_message(message:Message):
    if server is None: return
    member = server.get_member(message.author.id)
    channel = member
    if channel==None:return
    
    await client.wait_until_ready()
    
    async def greet_member(other):
        await send_welcome_message(other)
    async def complex_commands_component():
        if server.me.server_permissions.manage_roles:
            roles_valid_chart = defaultdict(lambda:False)
                
                
            commands = [
                
                ['assign',
                 'role',
                 lambda: {r.name:r 
                          for r in get_available_roles() 
                          if (r not in member.roles)},
                 partial(client.add_roles,member)],
                ['unassign',
                 'role',
                 lambda: {r.name:r 
                          for r in get_available_roles() 
                          if (r in member.roles)},
                 partial(client.remove_roles,member)],
                ["about",
                 "category",
                 lambda:{"studio": messages.about_studio,
                         "projects": messages.about_projects,},
                 partial(client.send_message,member)],
                ["help",
                 "command",
                 lambda:{"assign":
                         "assign yourself a role"+"\n".join(
                             "`assign {}`".format(r)
                             for r in get_available_roles() 
                             if (r not in member.roles))
                         },
                 partial(client.send_message,member)]
            ]
            if member is server.owner:
                commands +=[
                    ["greet",
                     "member",
                     lambda:{member.name: member
                             for member in server.members},
                     greet_member],
                ]
            
            for [cmd,category,get_elements,func] in commands:
                if content.startswith(cmd):
                    rest = content[len(cmd):]
                    if not rest or rest.startswith(' '):
                        rest = rest.lstrip()
                        print(category,get_elements(),rest)
                        elements = get_elements()
                        if len(elements)>0:
                            elements = [e for e in elements if e.startswith(rest)]
                            print(elements)
                            if len(elements)==1 and rest:
                                await func(get_elements()[elements[0]])
                                await client.add_reaction(message, "✅")
                            elif len(elements)>0:
                                possible_elements="\n".join(
                                    ' → `{}`'.format(role) 
                                    for role in reversed(elements)
                                )
                                await client.send_message(
                                    channel,
                                    "possible {}\n{}".format(
                                        category,
                                        possible_elements
                                    )
                                )
                            else:
                                await client.send_message(
                                    channel,
                                    "invalid role {0}ment\nuse `{0}` to see the possible {1}".format(
                                        cmd,
                                        category
                                    )
                                )
                        else:
                            await client.send_message(
                                channel,
                                "no possible {} to {}".format(category,cmd)
                            )
                        return True
                        
    async def owner_component():
        if member==server.owner:
            if content=='reload':
                import commands
                sent = await client.send_message(channel, "reload start")
                reload(commands)
                await client.edit_message(sent, "reload complete")
                await commands.on_ready()
                return True
                
    
                
    #check if message is a DM and check if author belongs to the correct server
    content = message.content
    top_role = server.me.top_role
    
    tests = [
        [lambda:(message.server is server or message.server is None) 
         and top_role!=server.default_role 
         and content.startswith(top_role.mention),
         lambda:content[len(top_role.mention):].lstrip()],
             
        [lambda:(message.server is server or message.server is None)  
         and content.startswith(server.me.mention),
         lambda:content[len(server.me.mention):].lstrip()],
             
        [lambda:message.server is None,
         lambda:content],
    ]
    components = [
        complex_commands_component,
        owner_component,
    ]
    for test,get_result in tests:
        if test():
            content=get_result()
            print(repr(content))
            if content == 'help':
                await send_help_message(member)
                return 
            elif content == 'hello':
                await send_welcome_message(member)
                return 
            elif content == 'toc':
                await client.send_message(member,messages.toc)
                return 
            elif content == 'instructions':
                await client.send_message(member,messages.instruction)
                return 
            for component in components:
                if await component():
                    return
            #NOTE remove this break later
            break # if nothing was caught 

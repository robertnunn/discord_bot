from discord.ext import commands
import json
from utils import sanitize_input
from .steam_utils import steam_id_re


@commands.command('steam')
async def steam(ctx, cmd='', arg=''):
    '''
    Provides basic steam functionality.
    Commands:
        register <arg>: Deals with registering steam ids and steam-related data
            args:
                [steam_id]: the steam ID you wish to be associated with your discord account (\d{17})
                'list': list users in the server who have steam IDs on file
    '''
    calling_user = ctx.message.author
    cmd = sanitize_input(cmd)
    arg = sanitize_input(arg)
    with open('users.json', 'r') as u:
                user_data = json.loads(u.read())
    if cmd.lower() == 'register':
        if match := steam_id_re.search(arg):
            new_steam_id = match.group(0)
            if user_data.get(str(ctx.message.author.id)):
                user_data[str(ctx.message.author.id)]['steam']['id'] = new_steam_id
                await calling_user.send(f'Successfully registered steam id {new_steam_id} with your discord account!')
            else:
                user_data[str(ctx.message.author.id)] = {'name': calling_user.display_name, 'steam': {'id': new_steam_id}}
                await calling_user.send(f'Successfully registered a new user and steam id {new_steam_id}!')
            
            with open('users.json', 'w') as u:
                u.write(json.dumps(user_data, indent=2))
        elif arg.lower() == 'list':
            registered = list()
            guild = ctx.guild
            print(guild.name)
            for k,v in user_data.items():
                print(f'checking {v["name"]}')
                if sid := v['steam'].get('id'):
                    print(sid)
                    if user := guild.get_member(int(k)):
                        print(user.display_name)
                        registered.append(user.display_name)
            registered.sort()
            registered.insert(0, 'The following users have steam IDs on file: ```')
            registered.append('```')
            await ctx.send('\n'.join(registered))
            
        else:
            await calling_user.send(f'Error: arg "{arg}" not a valid argument for the "register" command.')
            return
    else:
        await ctx.send(f'Error: unrecognized command `{cmd}`')
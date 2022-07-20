from discord.ext import commands
import json
from utils import sanitize_input
from .steam_utils import steam_id_re


@commands.command('steam')
async def steam(ctx, cmd='', arg=''):
    calling_user = ctx.message.author
    cmd = sanitize_input(cmd)
    arg = sanitize_input(arg)
    if cmd.lower() == 'register':
        if match := steam_id_re.search(arg):
            new_steam_id = match.group(0)
        else:
            await calling_user.send(f'Error: arg "{arg}" not a valid steam ID')
            return

        with open('users.json', 'r') as u:
            user_data = json.loads(u.read())
        
        if uid := user_data.get(str(ctx.message.author.id)):
            user_data[uid]['steam']['id'] = new_steam_id
            await calling_user.send(f'Successfully registered steam id {new_steam_id} with your discord account!')
        else:
            user_data[uid] = {'name': calling_user.display_name, 'steam': {'id': new_steam_id}}
            await calling_user.send(f'Successfully registered a new user and steam id {new_steam_id}!')
        
        with open('users.json', 'w') as u:
            u.write(json.dumps(user_data, indent=2))
    else:
        await ctx.send(f'Error: unrecognized command "{cmd}"')
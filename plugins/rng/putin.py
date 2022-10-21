import random
import os
import discord
from discord.ext import commands


@commands.command('putin')
async def putin_l_counter(ctx, cmd='', new_l=''):
    """
    Keep track of the many, many Ls that putin has taken since invading Ukraine!
    cmd is 'add': adds the following quoted string to the list
    cmd is 'all': shows all the Ls
    cmd is 'latest': show the latest L on the list
    Just "!putin": picks a random L
    """
    putin_file = f'{os.path.dirname(__file__)}/putin.txt'
    cmd = cmd.lower()
    if cmd == 'add' and new_l != '':
        with open(putin_file, 'a') as p:
            p.write(f'{new_l}\n')
        msg = f'Added: {new_l}'
    elif new_l == '' and cmd != 'add':
        with open(putin_file) as p:
            l_list = p.read().splitlines()
        msg = f"Putin has taken at least {len(l_list)} Ls since invading Ukraine. Here's"
        if cmd == 'latest':
            the_l = l_list[-1]
            msg = f"{msg} the latest putin L: {the_l}"
        elif cmd == 'all':
            all_ls = '\n'.join(l_list)
            all_ls = f'```\n{all_ls}```'
            msg = f"{msg} all of them.\n{all_ls}"
        else:
            the_l = random.choice(l_list)
            msg = f"{msg} a random putin L: {the_l}"

    if len(msg) <= 2000: # max length of discord message
        await ctx.send(msg)
    else:
        with open('plugins/rng/putin_all_msg.txt', 'w') as p:
            p.write(msg)
        f = discord.File('plugins/rng/putin_all_msg.txt')
        await ctx.send(file=f)

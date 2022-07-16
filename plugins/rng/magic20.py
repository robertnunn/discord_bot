import random
import os
from discord.ext import commands
from utils import sanitize_input

magic20_char_limit = 120

@commands.command()
async def magic20(ctx, cmd='', arg=''):
    """
    Roll a magic d20 (like an 8ball, but better)
    """
    with open(f'{os.path.dirname(__file__)}/magic20.txt') as f:
        lines = f.read().split('\n')
    try:
        lines.remove('')
    except:
        pass

    if cmd.lower() == 'add':
        ok_to_add = True
        arg = sanitize_input(arg)
        msg = list()
        if len(arg) > magic20_char_limit: # enforce character limit
            ok_to_add = False
            msg.append(f'Error: message is over the character limit ({magic20_char_limit}) by {len(arg)-magic20_char_limit} characters')
        
        if arg in lines:  # no dupes
            ok_to_add = False
            msg.append('Error: message `' + arg + '` is already in the list')
        
        if ok_to_add:  # this must come last
            with open('magic20.txt', 'a') as f:
                f.write('\n' + arg)
            msg = 'Added\n' + arg + f'\nto the list of responses as number {len(lines)+1}'
            
    elif cmd.lower() == 'del':
        try:  # basic error checking
            arg = int(arg)
            if 1 <= arg <= len(lines):  # more error checking
                removed = lines.pop(arg-1)
                with open('magic20.txt', 'w') as f:
                    f.write('\n'.join(lines))
                msg = f'Removed {removed} from the list'
            else:
                msg = f'Error: specified response is out of bounds'
        except:
            msg = f'Error: you must specify a number for the line you wish to delete. {arg} was not recognized as a numeric literal'
    else:
        msg = random.choice(lines)
        num = lines.index(msg)+1
        msg = f'{num}. {msg}'

    await ctx.send(msg)
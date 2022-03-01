import os
import json
from discord.ext import commands
import discord
import random
import re
from bs4 import BeautifulSoup as BS
import requests
import datetime
from dateutil.parser import parse


def load_creds(filepath):
    try:
        with open(filepath, "r") as c:
            credentials = json.loads(c.read())
        return credentials
    except Exception as e:
        print(f"Error: {e}.\nCredentials not loaded!")
        exit(1)


# bot setup
os.chdir(os.path.dirname(__file__))
cred_path = "bot_creds.json"
creds = load_creds(cred_path)
token = creds["TOKEN"]
bot = commands.Bot(command_prefix="!")
repo = creds["REPO"]

# regex for the dice rolling
separators_re = re.compile(r'[-\+x]')
dice_re = re.compile(r'^(\d+)d(\d+)!?$')
drop_dice_re = re.compile(r'^(\d+)?[L|H]$')
num_re = re.compile(r'^\d*$')

# magic20 rules
magic20_char_limit = 120

# gta bonus variables
gta_bonuses = dict()


@bot.command('putin')
async def putin_l_counter(ctx, cmd='', new_l=''):
    """
    Keep track of the many, many Ls that putin has taken since invading Ukraine!
    cmd is 'add': adds the following QUOTED string to the list
    cmd is 'all': shows all the Ls
    cmd is 'latest': show the latest L on the list
    Just "!putin": picks a random L
    """
    putin_file = 'putin.txt'
    cmd = cmd.lower()
    if cmd == 'add' and new_l != '':
        with open(putin_file, 'a') as p:
            p.write(f'{new_l}\n')
        msg = f'Added: {new_l}'
    elif new_l == '' and cmd != 'add':
        with open(putin_file) as p:
            l_list = p.read().splitlines()
        if cmd == 'latest':
            the_l = l_list[-1]
            msg = f"Putin has taken at least {len(l_list)} Ls since invading Ukraine. Here's the latest putin L: {the_l}"
        elif cmd == 'all':
            all_ls = '\n'.join(l_list)
            all_ls = f'```\n{all_ls}```'
            msg = f"Putin has taken at least {len(l_list)} Ls since invading Ukraine. Here's all of them. {all_ls}"
        else:
            the_l = random.choice(l_list)
            msg = f"Putin has taken at least {len(l_list)} Ls since invading Ukraine. Here's a random putin L: {the_l}"

    await ctx.send(msg)


@bot.command("randomvoice")
async def choose_random_voice_member(ctx):
    """
    Choose a random person from the voice chat the invoker is in.
    """
    calling_user = ctx.message.author
    voice_state = calling_user.voice  # none if not in VC
    if voice_state == None:
        msg = f"Error: {calling_user.display_name} is not in a voice channel"
    else:
        voice_channel = voice_state.channel
        user_list = voice_channel.members
        the_lucky_user = random.choice(user_list)
        msg = f"The lucky user is: {the_lucky_user.display_name}!"
    await ctx.send(msg)


@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")


@bot.command("liar")
async def say_liar(ctx):
    """
    Call someone a liar!
    """
    await ctx.send(
        "What a fucking liar dude! What a fucking weaselly little liar dude! What a fucking weaselly little liar dude! Holy shit dude! Holy fucking shit dude! Literally lying. Still lying!"
    )


def parse_dice(dice_str: str):
    """
    this block parses the string into operators and operands
    ex: '2d8+1d6+4' -> ['2d8', '+', '1d6', '+', '4']
    """
    chunks = list()
    while len(dice_str) > 0:
        boundary = separators_re.search(dice_str)
        if boundary == None:
            chunks.append(dice_str)
            break
        else:
            boundary = boundary.start()
        chunks.append(dice_str[:boundary])
        chunks.append(dice_str[boundary])
        dice_str = dice_str[boundary+1:]

    validated_chunks = list()
    for chunk in chunks:
        if separators_re.search(chunk) or dice_re.search(chunk) or drop_dice_re.search(chunk) or num_re.search(chunk):
            validated_chunks.append(chunk)

    return validated_chunks


def roll_dice(dice_str :str):
    """
    exploding dice add to the roll, so you always have the expected
    number of dice, but they can be higher
    ex: 2d6! could return [5, 16] if the second die exploded twice
    """
    results = list()
    total = 0
    exploding = True if dice_str[-1] == '!' else False
    dice_str = dice_str.replace('!', '')
    parsed_dice = dice_re.search(dice_str)
    num_dice = int(parsed_dice.group(1))
    num_sides = int(parsed_dice.group(2))
    
    for i in range(num_dice):
        result = random.randint(1, num_sides)
        temp = result
        while result == num_sides and exploding:
            result = random.randint(1, num_sides)
            temp += result
        result = temp
        results.append(result)

    return results


def chunk_roll(dice_str):
    """
    valid kinds of terms:
        dice roll: XdY(!)
        operator: +, -, x
        value modifier: \d*
        drop dice: \d*L
    """
    dice_chunks = parse_dice(dice_str)
    operator = ''
    high_or_low = None
    dict_list = list()
    # rolls, mod, drop_low, drop_high
    dice_dict = dict()
    # operators = ['+', '-', 'x']
    for term in dice_chunks:
        if dice_re.search(term):  # a dice roll; XdY
            if dice_dict != dict():
                dict_list.append(dice_dict)
            dice_dict = dict()
            dice_dict['roll'] = roll_dice(term)  # sorts asc, reverse=True for desc
            dice_dict['roll'].sort()
            dice_dict['roll_str'] = term
            if operator:
                dice_dict['roll_op'] = operator
            else:
                dice_dict['roll_op'] = ' '
            # print(f'dice: {dice_str}, rolls: {rolls}, total={sum(rolls)}')
        elif separators_re.search(term):  # an operator
            operator = term
        elif drop_dice_re.search(term):  # drop dice term
            if len(term) == 1:
                dice_dropped = 1
            else:
                dice_dropped = int(term[:-1])
            if term[-1] == "L":
                dice_dict['drop_low'] = dice_dropped
            elif term[-1] == "H":
                dice_dict['drop_high'] = dice_dropped
            # high_or_low = True if operand[-1] == 'H' else False
        elif num_re.search(term):  # modifier
            mod = f'{operator}{term}'
            try:
                dice_dict['mod'].append(mod)
            except KeyError:
                dice_dict['mod'] = [mod]
    dict_list.append(dice_dict)

    return (dict_list, ''.join(dice_chunks))


def dice_sum(roll_list):
    total = 0
    for i in roll_list:
        try:
            total += int(i)
        except:
            pass
    return total
    

def process_dict_list(dict_list):
    grand_total = 0
    total = 0
    rolled_dice = list()
    rolls = list()
    formatted_rolls = list()
    for roll in dict_list:
        total = 0
        try:  # do dice dropping first
            drop_low = roll['drop_low']
        except KeyError:
            drop_low = 0
        try:
            drop_high = roll['drop_high']
        except KeyError:
            drop_high = 0

        if (drop_high + drop_low) < len(roll['roll']):
            for i in range(drop_low):
                roll['roll'][i] = f'~~{roll["roll"][i]}~~'

            roll['roll'] = roll['roll'][::-1]
            for i in range(drop_high):
                roll['roll'][i] = f'~~{roll["roll"][i]}~~'
            roll['roll'] = roll['roll'][::-1]
        total = dice_sum(roll['roll'])

        try:
            for i in roll['mod']:  # apply mods from L->R, not PEMDAS
                try:
                    total += int(i)
                except:
                    total *= int(i[1:])
        except:
            roll['mod'] = ''
        
        try:
            grand_total += int(f'{roll["roll_op"]}{total}')
        except:
            grand_total *= int(f'{total}')

        if len(dict_list) > 1:
            spacer = 7*" "
            sub_roll = f'{roll["roll_op"]}{roll["roll_str"]}: '
        else:
            spacer = ''
            sub_roll = ''
        formatted_rolls.append(f'{spacer}{sub_roll}{roll["roll"]}{" ".join(roll["mod"])} = {total}')

    if len(formatted_rolls) > 1:
        # formatted_rolls.insert(0, '\n')
        formatted_rolls.append(f'Total = {grand_total}')
    return formatted_rolls


def do_the_needful(dice_str):
    chunks, validated_str = chunk_roll(dice_str)
    formatted_rolls = process_dict_list(chunks)
    line_sep = '\n'
    return (f'Rolled {validated_str}: {line_sep if len(formatted_rolls) > 1 else ""}{line_sep.join(formatted_rolls)}', validated_str)


@bot.command()
async def dice(ctx, dice_str: str):
    """
    Roll dice using standard dice syntax (2d6, 4d4+7)
    Dice may be chained (2d10+1d6+2)
    -XL to drop the lowest X dice (omitting X means X=1)
    -XH to drop the highest X dice (omitting X means X=1)
    XdY! to roll exploding dice
    """
    roll_str, rolled_dice = do_the_needful(dice_str)
    # roll_str = f'Rolled {rolled_dice}: {", ".join(results)} = {total}'
    if rolled_dice == dice_str:
        msg = roll_str
    else:
        msg = f'Error in dice string! The argument passed doesn\'t match what was rolled!\n{roll_str}'
    await ctx.send(msg)


@bot.command('8ball')
async def eight_ball(ctx):
    """
    Roll a magic eight-ball
    """
    with open('8ball.txt', 'r') as f:
        lines = f.read().split('\n')

    msg = random.choice(lines)
    await ctx.send(msg)


@bot.command()
async def dnd(ctx, adventure=0):
    """
    Get a random D&D adventure scenario (100 total)
    dnd <adventure> allows picking of a specific adventure
    """
    with open('dnd.txt', 'r') as f:
        adventures = f.read().split('\n')

    if 1 <= adventure <= 100:
        msg = adventure[adventure-1]
    else:
        msg = random.choice(adventures)

    await ctx.send(msg)


def sanitize_input(arg: str):
    # sanitizin' muh inputs
    arg = arg.replace('\n', '')
    exceptions = '!#$%&? ^*()-_=+[]{};:\'",./<>`~'
    for i in arg:
        if not i.isalnum() and i not in exceptions:
            arg = arg.replace(i, '')
    return arg


@bot.command()
async def magic20(ctx, cmd='', arg=''):
    """
    Roll a magic d20 (like an 8ball, but better)
    """
    with open('magic20.txt') as f:
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


@bot.command()
async def github(ctx):
    """
    Displays the repo for this bot.
    """
    await ctx.send(f'The repo for Jeeves is at:\n{repo}')


@bot.command()
async def gtabonus(ctx):
    """
    Show the current GTA Online weekly bonuses
    604,800s == 7 days
    """
    await ctx.send('When implemented, this will fetch and display the current bonuses for GTA Online.')


bot.run(token)
import os
import json
from discord.ext import commands
import random
import re


def load_creds(filepath):
    try:
        with open(filepath, "r") as c:
            credentials = json.loads(c.read())
        return credentials
    except Exception as e:
        print(f"Error: {e}.\nCredentials not loaded!")
        exit(1)


os.chdir(os.path.dirname(__file__))
cred_path = "bot_creds.json"
creds = load_creds(cred_path)
token = creds["TOKEN"]
bot = commands.Bot(command_prefix="!")


@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")


@bot.command("liar")
async def say_liar(ctx):
    """
    Call someone a liar!
    """
    await ctx.send(
        "What a fucking liar dude! What a fucking weaselly little liar dude! What a fucking weaselly little liar dude! Holy shit dude! Holy fucking shit dude! Literally lying. Still lying to his audience!"
    )


def parse_dice(dice_str: str):
    pattern = r'(\d+)d(\d+)([-\+]\d+)?'
    parsed = re.search(pattern, dice_str)
    if parsed == None:
        return f'Error parsing:{dice_str}'

    num_dice = int(parsed.group(1))
    num_sides = int(parsed.group(2))
    try:
        bonus = int(parsed.group(3))
        bonus_str = f'+{str(bonus)}' if bonus > 0 else str(bonus)
    except:
        bonus = 0
        bonus_str = ''
    results, total = roll_dice(num_dice, num_sides)
    total += bonus
    results.append(bonus_str)

    return (f'{parsed.group(0)}', results, total)


def roll_dice(num :int, sides :int):
    results = list()
    total = 0
    for i in range(num):
        result = random.randint(1, sides)
        results.append(str(result))
        total += result

    return (results, total)


@bot.command()
async def dice(ctx, dice_str: str):
    """
    Roll dice using standard dice syntax (2d6, 4d4+7)
    """
    rolled_dice, results, total = parse_dice(dice_str)
    msg = f'Rolled {rolled_dice}: {", ".join(results)} = {total}'
    await ctx.send(msg)


bot.run(token)
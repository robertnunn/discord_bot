import os
from discord.ext import commands
import discord
import importlib
from utils import load_creds

# bot setup
os.chdir(os.path.dirname(__file__))
cred_path = "bot_creds.json"
creds = load_creds(cred_path)
token = creds["TOKEN"]
repo = creds["REPO"]

intentions = discord.Intents().all()
bot = commands.Bot(command_prefix="!", intents=intentions)

# load plugins
plugs = dict()
for plugin in os.scandir('plugins'):
    if plugin.is_dir() and not plugin.name.startswith('__'):
        print(f'importing: {plugin.name}')
        plugs[plugin.name] = importlib.import_module(f'.{plugin.name}', 'plugins')

for k,v in plugs.items():
    for name, data in v.__dict__.items():
        if type(data) is commands.Command:
            bot.add_command(data)
            print(f'added: {data}')


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


@bot.command()
async def github(ctx):
    """
    Displays the repo for this bot.
    """
    await ctx.send(f'The repo for Jeeves is at:\n{repo}')


bot.run(token)
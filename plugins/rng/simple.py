# very simple RNG functions
import os
import random
from discord.ext import commands

@commands.command('8ball')
async def eight_ball(ctx):
    """
    Roll a magic eight-ball
    """
    with open(f'{os.path.dirname(__file__)}/8ball.txt', 'r') as f:
        lines = f.read().split('\n')

    msg = random.choice(lines)
    await ctx.send(msg)


@commands.command("randomvoice")
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


@commands.command()
async def dnd(ctx, adventure=0):
    """
    Get a random D&D adventure scenario (100 total)
    dnd <adventure> allows picking of a specific adventure
    """
    with open(f'{os.path.dirname(__file__)}/dnd.txt', 'r') as f:
        adventures = f.read().split('\n')

    if 1 <= adventure <= 100:
        msg = adventure[adventure-1]
    else:
        msg = random.choice(adventures)

    await ctx.send(msg)
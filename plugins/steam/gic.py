from discord.ext import commands
import json
import discord
from datetime import datetime
from .steam_utils import steam_key, get_games, get_game_mp_info


def mp_type_string(game_data: list, delimiter='|'):
    pvp = 'PvP' if 'PvP' in game_data else '   '
    pve = 'PvE' if 'PvE' in game_data else '   '
    rpt = 'RPT' if 'RPT' in game_data else '   '
    xp = 'XPlat' if 'XPlat' in game_data else '     '
    return f'{pve}{delimiter}{pvp}{delimiter}{rpt}{delimiter}{xp}'


@commands.command('gic')
async def games_in_common(ctx):
    '''
    See what games the people in the voice channel have in common. Requires a public steam profile and a steam ID (\d{17}) on file. Use "!steam register <steam id>" to register your steam id with this bot.

    May take a several seconds to resolve.
    '''
    # setup and error checking
    calling_user = ctx.message.author
    voice_state = calling_user.voice  # none if not in VC
    if voice_state == None:
        await ctx.send(f"Error: {calling_user.display_name} is not in a voice channel")
        return
    
    voice_channel = voice_state.channel
    discord_ids = {str(user.id) for user in voice_channel.members}
    if len(discord_ids) < 2:
        await ctx.send('Error: Must be in a voice channel with more than one person')
        return
    with open('users.json', 'r') as u:
        user_data = json.loads(u.read())
    with open('plugins/steam/gic.json', 'r') as g:
        gic_data = json.loads(g.read())
    steam_names = sorted([user.display_name for user in voice_channel.members if user_data[str(user.id)]['steam'].get('id')])

    steam_ids = {user_data[i]['steam']['id'] for i in discord_ids if user_data[i]['steam'].get('id')}
    if len(steam_ids) < 2:
        await ctx.send('Error: At least 2 users in the voice channel must have a steam id on file. Use `!steam register <steam id>` to register your steam ID with this bot')
        return

    msg = await ctx.send('Working...')
    
    # generate a set containing app_ids of all games in common (will contain SP-only games)
    net_games = set()  # just app_ids
    rpt_games = set()
    all_games = set()
    for i in steam_ids:
        user_games = get_games(i, steam_key, True)
        all_games.update(user_games)
        if len(net_games) == 0:
            net_games = user_games
        else:
            net_games.intersection_update(user_games)

    # steam apps that are MP and RPT so not everyone needs to own them
    for k,v in gic_data['multi_player'].items():
        if k in all_games:
            if 'RPT' in v['modes']:
                rpt_games.add(k)
    
    # if there's nothing in commmon
    if len(net_games) == 0 and len(rpt_games) == 0:
        msg = await ctx.edit('Error: There are no games that all users have in common')
        return

    # filter SP-only games and build string for MP games
    game_listing = list()
    rpt_listing = list()
    for game_id in net_games:
        if game_id in gic_data['single_player']:
            continue  # game is known to be SP only
        if game_id in gic_data['invalid']:  # game_id doesn't have any data associated with it
            continue
        
        if not gic_data['multi_player'].get(game_id):  # game data is not cached
            try:
                game_modes, game_name = get_game_mp_info(game_id)
            except:
                gic_data['invalid'].append(game_id)
                continue
            if game_name == '404':
                gic_data['404'].append(game_id)
                continue
            if len(game_modes) == 0:
                gic_data['single_player'].append(game_id)
                continue
            else:
                gic_data['multi_player'][game_id] = {'name': game_name, 'modes': game_modes}
                if 'RPT' in game_modes:
                    rpt_games.add(game_id)

        type_string = mp_type_string(gic_data['multi_player'][game_id]['modes'], '|')
        game_entry = (f'{type_string}', f'{gic_data["multi_player"][game_id]["name"]}')
        game_listing.append(game_entry)
        if 'RPT' in gic_data['multi_player'][game_id]['modes']:
            rpt_listing.append(game_entry)
    game_listing.sort(key=lambda x: x[1])
    rpt_listing.sort(key=lambda x: x[1])

    # write gic data in case there are new games
    with open('plugins/steam/gic.json', 'w') as g:
        g.write(json.dumps(gic_data, indent=2))

    # build msg string
    msg_list = [f'As of {datetime.now().isoformat()} (US Eastern Time), the following users:']
    for i in steam_names:
        msg_list.append(f'  {i}')
    msg_list.append('\n\nHave the following games in common:')
    msg_list.append('RPT: Remote Play Together; XPlat: Cross-Platform Multiplayer')
    for i in game_listing:
        msg_list.append(f'  {i[0]}: {i[1]}')
    msg_list.append('\n\nThe following games are available as RPT:')
    for i in rpt_listing:
        msg_list.append(f'  {i[0]}: {i[1]}')

    temp = '\n'.join(msg_list)
    with open('plugins/steam/gic.txt', 'w') as t:
        t.write(temp)
    await msg.delete()

    f = discord.File('plugins/steam/gic.txt')
    await ctx.send(file=f)
import requests
import json
import re
from utils import load_creds

steam_key = load_creds('bot_creds.json')['STEAM_API_KEY']
steam_id_re = re.compile(r'\d{17}')

def get_steam_apps():
    url = 'https://api.steampowered.com/ISteamApps/GetAppList/v2/'
    r = requests.get(url)
    try:
        r.raise_for_status()
    except Exception as e:
        return None #f'Error getting steam apps list. Error: {e}'
    app_list = json.loads(r.text)['applist']['apps']
    app_dict = {i['appid']: i['name'] for i in app_list}
    
    return app_dict


def get_games(steam_id: str, api_key: str, id_set_only=False):
    url = f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={api_key}&steamid={steam_id}&include_appinfo={str(not id_set_only)}'
    r = requests.get(url)
    try:
        r.raise_for_status()
    except:
        return None # f'Could not retrieve games data for steam id: "{steam_id}"'
    games = json.loads(r.text)['response']['games']
    if id_set_only:
        return {str(i['appid']) for i in games}
    else:
        return {str(i['appid']): {'name': i['name']} for i in games}


def get_game_mp_info(app_id: str):
    url = f'https://store.steampowered.com/api/appdetails?appids={app_id}'
    r = requests.get(url)
    try:
        r.raise_for_status()
    except:
        return None, '404'
    
    game_data = json.loads(r.text)
    mp_modes = list()
    sp = True
    try:
        game_name = game_data[app_id]['data']['name']
    except:
        return None
    for i in game_data[app_id]['data']['categories']:
        if i['id'] == 9:
            mp_modes.append('PvE')
        if i['id'] == 49:
            mp_modes.append('PvP')
        if i['id'] == 44:
            mp_modes.append('RPT')
        if i['id'] == 27:
            mp_modes.append('XPlat')
        if i['id'] == 1:
            sp = False

    if sp:
        mp_modes = list()

    return mp_modes, game_name
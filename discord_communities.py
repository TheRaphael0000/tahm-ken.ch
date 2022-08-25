import datetime
import urllib.request
import datetime
import json
from config import config

# initialize to old date, to be updated on the first request
last_update = datetime.datetime(year=1, month=1, day=1)
update_delta = datetime.timedelta(hours=2)

tahm_kench = "aHs3uDraNU"
communities = {
    tahm_kench: {},
    "zASN5E6RCv": {},
    "FJXAvqxw6T": {},
    "yapEVysv3b": {},
}


def _discord_api_request(url):
    request = urllib.request.Request(url)
    request.add_header("Authorization", f"Bot {config['discord_bot_token']}")
    request.add_header("User-Agent", "TKBOT (https://tahm-ken.ch, 1.0)")
    request.add_header("Content-Type", "application/json")
    response = urllib.request.urlopen(request)
    return request, response


def _update_discord_server_information(invite_id, discord_community):
    try:
        invite_url = f"https://discord.com/api/v10/invites/{invite_id}"
        _, response = _discord_api_request(invite_url)
        data = response.read().decode("utf-8")
        data = json.loads(data)
        discord_community |= data
    except Exception as e:
        print(e)
        print(e.read())


def _update_discord():
    for invite_id, discord_community in communities.items():
        _update_discord_server_information(invite_id, discord_community)


def get_discord_communities():
    global last_update
    if last_update + update_delta < datetime.datetime.now():
        _update_discord()
        last_update = datetime.datetime.now()
    return communities, tahm_kench

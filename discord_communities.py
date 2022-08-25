import datetime
import urllib.request
from urllib.request import Request
import datetime
import json
from config import config

discord_last_update = datetime.datetime(year=1, month=1, day=1)
discord_update_delta = datetime.timedelta(hours=2)
discord_communities = {
    "aHs3uDraNU": {},
    "zASN5E6RCv": {},
    "FJXAvqxw6T": {},
    "yapEVysv3b": {},
}

discord_tahm_kench = "aHs3uDraNU"


def update_discord_server_information(invite_id, discord_community):
    try:
        invite = f"https://discord.com/api/v10/invites/{invite_id}"
        r = Request(invite)
        r.add_header("Authorization", f"Bot {config['discord_bot_token']}")
        r.add_header("User-Agent", "TKBOT (https://tahm-ken.ch, 1.0)")
        r.add_header("Content-Type", "application/json")
        response = urllib.request.urlopen(r)
        data = response.read().decode("utf-8")
        data = json.loads(data)
        discord_community |= data
    except Exception as e:
        print(e)
        print(e.read())


def update_discord():
    for invite_id, discord_community in discord_communities.items():
        update_discord_server_information(invite_id, discord_community)


def get_discord_communities():
    global discord_last_update
    if discord_last_update + discord_update_delta < datetime.datetime.now():
        update_discord()
        discord_last_update = datetime.datetime.now()

    return discord_communities, discord_tahm_kench

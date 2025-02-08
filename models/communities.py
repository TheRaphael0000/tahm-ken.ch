import datetime
import urllib.request
import datetime
import json
import os

# initialize to old date, to be updated on the first request
last_update = datetime.datetime(year=1, month=1, day=1)
update_delta = datetime.timedelta(hours=2)

communities = {
    "aHs3uDraNU": {},
    "https://challenges.darkintaqt.com/": {
        "title": "Challenge Tracker",
        "img": "/static/img/challenges_darkintaqt_com.png",
        "text": "League of Legends Challenge Tracker & Leaderboards by DarkIntaqt.com",
        "url": "https://challenges.darkintaqt.com/",
        "type": "Website",
    },
    "zASN5E6RCv": {},
    "FJXAvqxw6T": {},
    "yapEVysv3b": {},
    "cKGS6ASyuZ": {},
}


def _discord_api_request(url):
    request = urllib.request.Request(url)
    request.add_header("User-Agent", "TKBOT (https://tahm-ken.ch, 1.0)")
    request.add_header("Content-Type", "application/json")
    response = urllib.request.urlopen(request)
    return request, response


def _update_discord_server_information(invite_id, community):
    try:
        invite_url = f"https://discord.com/api/v10/invites/{invite_id}"
        _, response = _discord_api_request(invite_url)
        data = response.read().decode("utf-8")
        data = json.loads(data)
        print(
            f"Loaded: {data['guild']['name']}, expire at {data['expires_at']}")
        community['title'] = data['guild']['name']
        community['img'] = f"https://cdn.discordapp.com/icons/{
            data['guild']['id']}/{data['guild']['icon']}.jpg?size=256"
        community['text'] = data['guild']['description']
        community['url'] = f"https://discord.gg/{invite_id}"
        community['type'] = "Discord"

    except Exception as e:
        pass


def _update_discord():
    for key, community in communities.items():
        if len(key) == 10:
            _update_discord_server_information(key, community)


def get_communities():
    global last_update
    if last_update + update_delta < datetime.datetime.now():
        _update_discord()
        last_update = datetime.datetime.now()
    return communities

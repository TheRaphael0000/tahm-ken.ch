import requests
from config import config

riot_endpoint = "https://europe.api.riotgames.com"
league_endpoint = "https://euw1.api.riotgames.com"


def api_request(url, is_riot_endpoint=False):
    if is_riot_endpoint:
        url = f"{riot_endpoint}{url}"
    else:
        url = f"{league_endpoint}{url}"

    response = requests.get(
        url, headers={"X-Riot-Token": config["riot_api_key"]})
    data = response.json()
    return data

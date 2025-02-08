import requests
import os
from .regions import regions_by_id

riot_endpoint = "https://europe.api.riotgames.com"
league_endpoint = "https://{0}.api.riotgames.com"


def api_request(url, region=None):
    if region is None:
        url = f"{riot_endpoint}{url}"
    else:
        endpoint = league_endpoint.format(
            regions_by_id[region]["id"])
        url = f"{endpoint}{url}"

    print(url)
    response = requests.get(
        url, headers={"X-Riot-Token": os.getenv("riot_api_key")})
    data = response.json()
    return data

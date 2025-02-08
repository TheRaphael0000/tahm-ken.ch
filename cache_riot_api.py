import json
from pathlib import Path
from dotenv import load_dotenv

from models.riot_api import api_request

FOLDER = Path("static/cache/riot_api/")

challenges_config = api_request(
    "/lol/challenges/v1/challenges/config", region="EUW1")

try:
    FOLDER.mkdir(parents=True)
except:
    pass

json.dump(challenges_config, open(
    FOLDER / Path("challenges_config.json"), "w"))

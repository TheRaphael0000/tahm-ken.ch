from config import config
import json
from pathlib import Path

from models.riot_api import api_request

FOLDER = Path("static/api_cache/")

challenges_config = api_request("/lol/challenges/v1/challenges/config", region="EUW1")

try:
    FOLDER.mkdir(parents=True)
except:
    pass

json.dump(challenges_config, open(
    FOLDER / Path("challenges_config.json"), "w"))

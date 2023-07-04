from riotwatcher import LolWatcher
from riotwatcher import ApiError
from config import config
import json
from pathlib import Path

FOLDER = Path("static/api_cache/")

lol_watcher = LolWatcher(config["riot_api_key"])
challenges_config = lol_watcher.challenges.config("EUW1")

try:
    FOLDER.mkdir(parents=True)
except:
    pass

json.dump(challenges_config, open(FOLDER / Path("challenges_config.json"), "w"))
import json
import shutil
from pathlib import Path

config_file = Path("config.json")
config_sample_file = Path("config_sample.json")

if not config_file.is_file():
    if not config_sample_file.is_file():
        print("no config file")
        exit()
    else:
        shutil.copyfile(config_sample_file, config_file)

config = json.load(open(config_file, "rb"))
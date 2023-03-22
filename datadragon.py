import urllib.request
from urllib.parse import urlparse
import json
from pathlib import Path

endpoint = "https://ddragon.leagueoflegends.com"
folder = "static/datadragon_cache"

def dl(url, subfolder=""):
    print(url)
    url = endpoint + url
    u_r_l = urlparse(url)
    filename = u_r_l.path.split("/")[-1]
    local_filename, headers = urllib.request.urlretrieve(url)
    data = open(local_filename, "rb").read()
    try:
        Path(f"{folder}{subfolder}").mkdir(parents=True)
    except:
        pass
    open(f"{folder}{subfolder}/{filename}", "wb").write(data)


print("data dragon cache helper")

dl("/api/versions.json")
lversion = json.load(open(f"{folder}/versions.json"))[0]

print(f"latest version : {lversion}")

cversion = None
try:
    cversion = open(f"{folder}/version", "r").read()
except:
    pass


if lversion == cversion:
    print(f"data dragon cache already up to date")
    exit()

print(f"downloading files for version {lversion}")


dl(f"/cdn/{lversion}/data/en_US/champion.json")
champions = json.load(open(f"{folder}/champion.json", "rb"))
for id, champion in champions["data"].items():
    image_url = f"/cdn/{lversion}/img/champion/{champion['image']['full']}"
    dl(image_url, subfolder="/champions_img")

open(f"{folder}/version", "w").write(lversion)
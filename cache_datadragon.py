import urllib.request
from urllib.parse import urlparse
import json
from pathlib import Path

endpoint = "https://ddragon.leagueoflegends.com"
folder = "static/cache/datadragon"


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
latest_version = json.load(open(f"{folder}/versions.json"))[0]

print(f"latest version : {latest_version}")

current_version = None
try:
    current_version = open(f"{folder}/version", "r").read()
except Exception as e:
    print(e)

print(f"{folder}/version")

if latest_version == current_version:
    print(f"data dragon cache already up to date")
    exit()

print(f"downloading files for version {latest_version}")


dl(f"/cdn/{latest_version}/data/en_US/champion.json")
champions = json.load(open(f"{folder}/champion.json", "rb"))
for id, champion in champions["data"].items():
    image_url = f"/cdn/{latest_version}/img/champion/{champion['image']['full']}"
    dl(image_url, subfolder="/champions_img")

open(f"{folder}/version", "w").write(latest_version)

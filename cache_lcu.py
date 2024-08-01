from pathlib import Path
from requests import get, auth
import json
from pprint import pprint
from collections import defaultdict

game_path = "C:/Riot Games/League of Legends/"
certif_path = "./riotgames.pem"


def get_endpoint(game_folder):
    values = open(game_folder / Path("lockfile")).read().split(":")
    return (f"{values[4]}://127.0.0.1:{values[2]}", ("riot", values[3]))


def query(route):
    try:
        url, creds = get_endpoint(Path(game_path))
        basic = auth.HTTPBasicAuth(*creds)
        answer = get(url + route, auth=basic, verify=Path(certif_path))
        return json.loads(answer.content)
    except FileNotFoundError:
        print("Client not open")


challenges_template = json.load(
    open("static/cache_lcu/challenges_template.json", "r"))
challenges = query(f"/lol-challenges/v1/challenges/local-player")
champions = json.load(
    open("static/cache_datadragon/champion.json", "rb"))["data"]

valid_groups = ["Harmony", "Globetrotter"]

champion_key_to_id = {c["key"]: c["id"] for c in champions.values()}

challenges_index_lookup = {t["id"]: i for i,
                           t in enumerate(challenges_template)}

for challenge in challenges.values():
    if challenge["capstoneGroupName"] not in valid_groups or challenge["idListType"] != "CHAMPION":
        continue
    id_ = challenge["id"]
    index = challenges_index_lookup[id_]
    challenges_template[index]["_"] = challenge["name"]

    for champion_key in challenge["availableIds"]:
        # there are a lot of garbage ids here now, riot wtf??
        if str(champion_key) not in champion_key_to_id:
            print(f"Error with id {champion_key}")
            continue
        c = champion_key_to_id[str(champion_key)]
        challenges_template[index]["champions"].append(c)
    challenges_template[index]["champions"].sort()

# add variety is overrated
champions_by_tag = defaultdict(list)
for champion, data in champions.items():
    for tag in data["tags"]:
        champions_by_tag[tag].append(champion)
champions_by_tag = dict(champions_by_tag)

for tag, champions in champions_by_tag.items():
    challenge = {
        "id": 303408,
        "_": "Variety's Overrated",
        "qte": 5,
        "label": tag,
        "champions": champions,
    }
    challenges_template.append(challenge)

json.dump(challenges_template, open(
    "static/cache_lcu/challenges.json", "w"), indent=4)

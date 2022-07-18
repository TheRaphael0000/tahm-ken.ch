import json
from collections import defaultdict

champions = json.load(
    open("static/datadragon_cache/champion.json", "rb"))["data"]

champions_by_tag = defaultdict(list)


for champion, data in champions.items():
    for tag in data["tags"]:
        champions_by_tag[tag].append(champion)


champions_by_tag = dict(champions_by_tag)

challenges = []
for tag, champions in champions_by_tag.items():
    challenge = {
        "challenge_name": f"Variety's Overrated",
        "label": tag,
        "champions": champions,
        "qte": "5"
    }
    challenges.append(challenge)

print(json.dumps(challenges))

from flask import Flask
from flask import render_template
from flask import redirect
import json
from collections import defaultdict
import random
from riotwatcher import LolWatcher, ApiError
from config import config
from constants import regions, ranks, default_region
import urllib.parse

# create the flask app
app = Flask(__name__, static_url_path="/static")

# load challenges data
challenges = json.load(open("static/challenges.json", "r"))
for c in challenges:
    c["champions_l"] = len(c["champions"])
challenges.sort(key=lambda l: -l["champions_l"])
challenges.sort(key=lambda l: l["qte"])

# add the challenges data from the riot api to the json data
try:
    lol_watcher = None
    challenges_config = None
    lol_watcher = LolWatcher(config["riot_api_key"])
    challenges_config = lol_watcher.challenges.config(default_region)
    challenges_config = {c["id"]: c for c in challenges_config}
except ValueError:
    print("No Riot API key provided")
except ApiError:
    print("This Riot API key can't access the challenges scope")

for challenge in challenges:
    challenge["config"] = challenges_config[challenge["riot_id"]]

# load champions data
champions = json.load(
    open("static/datadragon_cache/champion.json", "rb"))["data"]
champions_keys = sorted(champions, key=lambda c: champions[c]["name"])

# load the pre-calculated compositions
compositions = json.load(open("static/compositions.json", "r"))


@app.route("/")
def main():
    return redirect("/tool")


@app.route("/tool", defaults={"region": default_region, "summoner": ""})
@app.route("/tool/<region>/", defaults={"summoner": ""})
@app.route("/tool/<region>/<summoner>/")
def tool(region, summoner):
    args = {
        "champions": enumerate(champions_keys),
        "challenges": enumerate(challenges),
        "compositions": list(compositions.keys()),
        "regions": regions,
        "region": region,
        "summoner": summoner,
        "summoner_progress": None,
    }
    try:
        if region and summoner and lol_watcher:
            summoner = lol_watcher.summoner.by_name(region, summoner)
            summoner_challenges_infos = lol_watcher.challenges.by_puuid(
                region, summoner['puuid'])

            summoner_challenges_by_id = {
                c["challengeId"]: c for c in summoner_challenges_infos["challenges"]}

            challenges_for_this_summoner = {}
            for c in challenges:
                id = c["riot_id"]
                if id in summoner_challenges_by_id:
                    summoner_challenges_progress = summoner_challenges_by_id[id]
                    challenges_for_this_summoner
                    challenge_for_this_summoner = {
                        "level": summoner_challenges_progress["level"],
                        "value": int(summoner_challenges_progress["value"]),
                    }
                else:
                    challenge_for_this_summoner = {
                        "level": "UNRANKED",
                        "value": 0,
                    }
                challenges_for_this_summoner[id] = challenge_for_this_summoner

            args["summoner_progress"] = challenges_for_this_summoner
    except Exception as e:
        print(e)

    return render_template("tool.html", **args)


@app.route("/compositions/<challenge>")
def comps(challenge):
    by_number = defaultdict(list)
    comps = compositions[challenge]
    # limit large challenges
    limit = 8000
    if len(comps) > limit:
        random.shuffle(comps)
        comps = comps[0:limit]
        comps = [(sorted(comp), comp_challenge)
                 for comp, comp_challenge in comps]
        comps.sort()
    champions_available = set()
    for comp, chall in comps:
        by_number[len(chall)].append((comp, chall))
        champions_available |= set(comp)
    champions_ = {c: d for c, d in champions.items()
                  if c in champions_available}

    args = {
        "by_number": by_number,
        "challenge_name": challenge,
        "compositions": list(compositions.keys()),
        "champions": champions_,
    }
    return render_template("compositions.html", **args)


@app.route("/challenge_intersection/<challenges_id>")
def challenge_intersection(challenges_id):
    challenges_id = [int(s) for s in challenges_id.split(",")]
    challenges_champions = [set(challenges[ci]["champions"])
                            for ci in challenges_id]
    u = set.intersection(*challenges_champions)

    response = {
        "intersection": list(u),
        "challenges_additional_intersection": list()
    }
    for i, c in enumerate(challenges):
        s = set(c["champions"])
        uc = u.intersection(s)
        response["challenges_additional_intersection"].append([i, len(uc)])

    return json.dumps(response)


@app.route("/champions_selected/<champions>")
def champions_selected(champions=""):
    champions = set(champions.split(","))

    valid_challenges = {}

    for i, c in enumerate(challenges):
        set_champions = set(c["champions"])
        current_selection = len(set_champions.intersection(champions))
        valid_challenges[i] = current_selection

    return json.dumps(valid_challenges)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)

from flask import Flask
from flask import render_template
import json
from collections import defaultdict
import random


app = Flask(__name__, static_url_path='/static')

challenges = json.load(open("static/challenges.json", "r"))
for c in challenges:
    c["champions_l"] = len(c["champions"])
challenges.sort(key=lambda l: -l["champions_l"])
challenges.sort(key=lambda l: l["qte"])


champions = json.load(
    open("static/datadragon_cache/champion.json", "rb"))["data"]
champions_keys = sorted(champions, key=lambda c: champions[c]["name"])

compositions = json.load(open("static/compositions.json", "r"))


@app.route("/")
def main():
    return render_template('main.html', champions=enumerate(champions_keys), challenges=enumerate(challenges), compositions=list(compositions.keys()))


@app.route("/compositions/<challenge>")
def comps(challenge):
    by_number = defaultdict(list)
    comps = compositions[challenge]
    # limit large challenges
    limit = 8000
    if len(comps) > limit:
        random.shuffle(comps)
        comps = comps[0:limit]
        comps = [(sorted(comp), comp_challenge) for comp, comp_challenge in comps]
        comps.sort()
    champions_available = set()
    for comp, chall in comps:
        by_number[len(chall)].append((comp, chall))
        champions_available |= set(comp)
    champions_ = {c: d for c, d in champions.items()
                  if c in champions_available}
    return render_template('compositions.html', by_number=by_number, challenge_name=challenge, compositions=list(compositions.keys()), champions=champions_)


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
def champions_selected(champions):
    champions = set(champions.split(","))

    valid_challenges = []

    for i, c in enumerate(challenges):
        set_champions = set(c["champions"])
        if len(set_champions.intersection(champions)) >= int(c["qte"]):
            valid_challenges.append(i)

    return json.dumps(valid_challenges)


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000, debug=True)

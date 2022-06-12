from flask import Flask
from flask import render_template
import json


app = Flask(__name__, static_url_path='/static')

challenges = json.load(open("challenges.json", "r"))

champions = set()
for c in challenges:
    champions |= set(c["champions"])

    c["champions_l"] = len(c["champions"])
champions = list(champions)
champions.sort()


@app.route("/")
def main():
    challenges.sort(key=lambda l: -l["champions_l"])
    challenges.sort(key=lambda l: l["qte"])
    return render_template('main.html', champions=enumerate(champions), challenges=enumerate(challenges))


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
        s = set(c["champions"])
        if champions <= s:
            valid_challenges.append(i)

    return json.dumps(valid_challenges)

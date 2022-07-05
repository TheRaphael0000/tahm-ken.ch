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
challenges.sort(key=lambda l: -l["champions_l"])
challenges.sort(key=lambda l: l["qte"])


@app.route("/")
def main():
    return render_template('main.html', champions=enumerate(champions), challenges=enumerate(challenges))


@app.route("/comps")
def comps():
    comps = [
        ("Summoners on the Rift", ["Maokai", "Ziggs", "Kled", "Zyra", "Elise"]),
        ("Summoners on the Rift", ["Maokai", "Ziggs", "Kled", "Zyra", "Lissandra"]),
        ("Summoners on the Rift", ["Maokai", "Ziggs", "Kled", "Zyra", "Kalista"]),
        ("Summoners on the Rift", ["Maokai", "Ziggs", "Kled", "Zyra", "Kindred"]),
        ("Summoners on the Rift", ["Maokai", "Ziggs", "Kled", "Zyra", "Malzahar"]),
        ("Summoners on the Rift", ["Maokai", "Ziggs", "Kled", "Zyra", "Zed"]),
        ("Summoners on the Rift", ["Maokai", "Ziggs", "Kled", "Lissandra", "Shaco"]),
        ("We Protec", ["Maokai", "Ziggs", "Bard", "Nidalee", "Alistar"]),
        ("We Protec", ["Maokai", "Ziggs", "Bard", "Nidalee", "TahmKench"]),
    ]
    return render_template('comps.html', comps=comps)


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

    print(champions)

    for i, c in enumerate(challenges):
        set_champions = set(c["champions"])
        print(c["challenge_name"], c["qte"], set_champions)
        if len(set_champions.intersection(champions)) >= int(c["qte"]):
            valid_challenges.append(i)

    return json.dumps(valid_challenges)


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000, debug=True)

import json
import random
from collections import defaultdict

from flask import Flask
from flask import abort
from flask import render_template
from flask import redirect

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from riotwatcher import LolWatcher
from riotwatcher import ApiError

from constants import regions
from constants import ranks
from constants import roles
from constants import default_region
from challenges_tools import get_custom_optimized_compositions
from challenges_tools import get_summoner_challenges_infos
from challenges_tools import challenges
from challenges_tools import champions
from challenges_tools import champions_keys
from challenges_tools import lol_watcher
from tk_quotes import RandomQuotes

# create the flask app
app = Flask(__name__, static_url_path="/static")
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 60 * 60
# create the request limiter
limiter = Limiter(app, key_func=get_remote_address)

# load the pre-calculated compositions
compositions = json.load(open("static/compositions.json", "r"))

# variables which are required for the layout
layout = {
    "quote": RandomQuotes(),
    "compositions": [(c, c.replace(" ", "_")) for c in compositions.keys()],
}


@app.route("/")
def main():
    return redirect("/challenges_intersection")


# temporary redirection for old route
@app.route('/tool/', defaults={'path': ''})
@app.route('/tool/<path:path>')
def route_tool(path):
    return redirect("/".join(["/challenges_intersection", path]))


def get_args_challenges_intersection(region, summoner):
    return {
        "champions": champions,
        "champions_keys": enumerate(champions_keys),
        "challenges": enumerate(challenges),
        "regions": regions,
        "region": region,
        "summoner": summoner,
        "summoner_progress": None,
        "layout": layout,
    }


@app.route("/challenges_intersection")
def route_challenges_intersection():
    args = get_args_challenges_intersection("EUW1", "")
    return render_template("challenges_intersection.html", **args)


@app.route("/challenges_intersection/<region>/<summoner>")
@limiter.limit("6/minutes")
def route_challenges_intersection_summoner(region, summoner):
    args = get_args_challenges_intersection(region, summoner)
    try:
        args["summoner_progress"], args["total_points"] = get_summoner_challenges_infos(
            region, summoner)
    except Exception as e:
        args["error"] = "Couldn't find the summoner"
    return render_template("challenges_intersection.html", **args)


def comps_processing(comps):
    # limit large challenges
    by_number = defaultdict(list)
    limit = 8000
    comps.sort(key=lambda c: -len(c[-1]))
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
        "champions": champions_,
        "layout": layout,
    }
    return args


@app.route("/compositions/<challenge>")
def route_compositions(challenge):
    challenge = challenge.replace("_", " ")
    try:
        comps = compositions[challenge]
    except:
        return abort(404)

    args = comps_processing(comps)
    args["challenge_name"] = challenge
    return render_template("compositions.html", **args)


@app.route("/custom_compositions/<region>/<summoners_names>")
@limiter.limit("2/minutes")
def route_custom_compositions(region, summoners_names):
    try:
        summoners_names = summoners_names.split(",")
        if len({name for name in summoners_names if len(name) >= 2}) != 5:
            raise Exception(f"Require five valid distinct summoners name.")
        comps = get_custom_optimized_compositions(region, summoners_names)
    except Exception as e:
        args = {
            "roles": enumerate(roles),
            "regions": regions,
            "region": default_region,
            "error": e,
            "layout": layout,
        }
        return render_template("custom_compositions.html", **args)

    args = comps_processing(comps)
    args["challenge_name"] = f"Custom composition for '{', '.join(summoners_names)}'"
    return render_template("compositions.html", **args)


@app.route("/custom_compositions")
def route_custom_compositions_wizard():
    args = {
        "roles": enumerate(roles),
        "regions": regions,
        "region": default_region,
        "layout": layout,
    }
    return render_template("custom_compositions.html", **args)


@app.route("/challenge_intersection/<challenges_id>")
def route_challenge_intersection(challenges_id):
    try:
        challenges_id = [int(s) for s in challenges_id.split(",")]
        challenges_champions = [set(challenges[ci]["champions"])
                                for ci in challenges_id]
    except:
        return abort(404)
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
def route_champions_selected(champions=""):
    try:
        champions = set(champions.split(","))

        valid_challenges = {}

        for i, c in enumerate(challenges):
            set_champions = set(c["champions"])
            current_selection = len(set_champions.intersection(champions))
            valid_challenges[i] = current_selection
    except:
        return abort(404)

    return json.dumps(valid_challenges)


@app.route("/how_to_use")
def route_how_to_use():
    args = {
        "layout": layout,
    }
    return render_template("how_to_use.html", **args)


@app.route("/faq")
def route_faq():
    args = {
        "layout": layout,
    }
    return render_template("faq.html", **args)


@app.errorhandler(404)
def route_page_not_found(e):
    args = {
        "layout": layout,
    }
    return render_template('404.html', **args), 404


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)

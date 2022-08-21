from collections import defaultdict
import json
import random
import urllib.request
import threading

import bs4

from flask import Flask
from flask import abort
from flask import render_template
from flask import redirect

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from constants import regions
from constants import roles
from constants import default_region

from challenges_tools import get_custom_optimized_compositions
from challenges_tools import get_summoner_challenges_infos
from challenges_tools import challenges
from challenges_tools import challenges_groups
from challenges_tools import challenges_config
from challenges_tools import champions
from challenges_tools import champions_alphabetical

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
    "compositions": sorted([(c, c.replace(" ", "_")) for c in compositions.keys()]),
    "language": "en_US",
}


@app.route("/")
def main():
    return redirect("/challenges_intersection")


def get_args_challenges_intersection(region, summoner):
    return {
        "champions": champions,
        "champions_alphabetical": champions_alphabetical,
        "challenges": enumerate(challenges),
        "challenges_config": challenges_config,
        "regions": regions,
        "region": region,
        "summoner": summoner,
        "summoner_challenges": None,
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
        summoner_challenges, total_points = get_summoner_challenges_infos(
            region, summoner)
        args |= {
            "summoner_challenges": summoner_challenges,
            "total_points": total_points,
        }
    except Exception as e:
        args["error"] = f"Couldn't find the summoner {e}"
        raise Exception(e)
    return render_template("challenges_intersection.html", **args)


def comps_processing(comps):
    # limit large challenges
    by_number = defaultdict(list)
    limit = 8000
    if len(comps) > limit:
        random.shuffle(comps)
        comps = comps[0:limit]
        comps = [(sorted(comp), comp_challenge)
                 for comp, comp_challenge in comps]
        comps.sort()
    champions_available = set()
    for comp, challenges, stupidity_level in comps:
        comp = [comp[role] for role in roles]
        by_number[len(challenges)].append((comp, challenges, stupidity_level))
        champions_available |= set(comp)
    champions_ = {c: d for c, d in champions.items()
                  if c in champions_available}

    by_number = list(by_number.items())
    by_number.sort(key=lambda l: -l[0])
    by_number = dict(by_number)

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


@app.route("/faq")
def route_faq():
    args = {
        "layout": layout,
    }
    return render_template("faq.html", **args)


def scrap_discord_server_information(community):
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent', 'Mozilla/5.0')]

    with opener.open(community["link"]) as f:
        html_doc = f.read()
        soup = bs4.BeautifulSoup(html_doc, "html.parser")

        community["name"] = soup.find("title").text
        community["image"] = soup.find("meta", property="og:image")["content"]


@app.route("/communities")
def route_communities():
    args = {
        "layout": layout,
        "tahm_kench": {
            "message": "The Tahm-Ken.ch official discord server.",
            "link": "https://discord.gg/aHs3uDraNU",
        },
        "communities": [
            {
                "message": "High Mastery is a discord focused primarily on farming challenges in the most efficient way possible with tons of community resources to aid you in your goals",
                "link": "https://discord.gg/zASN5E6RCv",
            },
            {
                "message": "League discord to group up with players to complete challenges and discuss everything about League.",
                "link": "https://discord.gg/FJXAvqxw6T",
            }
        ]
    }

    processes = []
    for community in args["communities"] + [args["tahm_kench"]]:
        process = threading.Thread(
            target=scrap_discord_server_information, args=[community])
        process.start()
        processes.append(process)

    for process in processes:
        process.join()

    return render_template("communities.html", **args)


@app.errorhandler(404)
def route_page_not_found():
    args = {
        "layout": layout,
    }
    return render_template('404.html', **args), 404


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)

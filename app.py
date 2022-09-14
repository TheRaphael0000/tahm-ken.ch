from collections import defaultdict
import json
import random

from flask import Flask
from flask import abort
from flask import render_template
from flask import redirect
from flask import request
from flask import session

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import config

from regions import regions
from regions import regions_by_abbreviation
from regions import get_region_from_ip

from constants import roles

from challenges_tools import compute_challenges_priority_scores, get_custom_optimized_compositions
from challenges_tools import get_summoner_challenges_info
from challenges_tools import challenges_groups
from challenges_tools import challenges_data
from challenges_tools import challenges_config
from challenges_tools import find_challenges_details
from challenges_tools import champions
from challenges_tools import champions_alphabetical

from champions_roles import best_fit_roles

from tk_quotes import RandomQuotes

from discord_communities import get_discord_communities

# create the flask app
app = Flask(__name__, static_url_path="/static")
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 60 * 60
app.secret_key = config["app_secret_key"]

# create the request limiter
limiter = Limiter(app, key_func=get_remote_address)

language = "en_US"
multisearch_max_size = 8

# load the pre-calculated compositions
compositions = json.load(open("static/compositions.json", "r"))

compositions_names_routes = {}
for key in compositions.keys():
    try:
        name = challenges_config[int(key)]["localizedNames"][language]["name"]
    except:
        name = key
    url = name.replace(" ", "_")
    compositions_names_routes[url] = (name, key)

# variables which are required for the layout
layout = {
    "quote": RandomQuotes(),
    "compositions": compositions_names_routes,
    "language": language,
}


def get_default_region():
    # store the region in the session
    # to avoid having to lookup multiple times
    if "default_region" in session:
        default_region = session["default_region"]
    else:
        default_region = get_region_from_ip(request.remote_addr)
        session["default_region"] = default_region
    return default_region


@app.route("/")
def main():
    return redirect("/challenges_intersection")


def args_challenges_intersection(region, summoner):
    return {
        "champions": champions,
        "champions_alphabetical": champions_alphabetical,
        "challenges_data": challenges_data,
        "challenges_groups": challenges_groups,
        "challenges_config": challenges_config,
        "regions": regions,
        "region": region,
        "summoner": summoner,
        "summoner_challenges": None,
        "layout": layout,
    }


@app.route("/challenges_intersection")
def route_challenges_intersection():
    args = args_challenges_intersection(get_default_region(), "")
    return render_template("challenges_intersection.html", **args)


@app.route("/challenges_intersection/<region>/<summoner>")
@limiter.limit("6/minutes")
def route_challenges_intersection_summoner(region, summoner):
    try:
        region = regions_by_abbreviation[region]
    except:
        return redirect("/challenges_intersection")
    summoner = summoner.replace("_", " ")
    args = args_challenges_intersection(region, summoner)
    try:
        challenges_info = get_summoner_challenges_info(region["id"], summoner)
        args |= challenges_info
    except Exception as e:
        args["error"] = f"Couldn't find '{summoner}' on {region['abbreviation']}"
    return render_template("challenges_intersection.html", **args)


def comps_processing(comps):
    # limit large challenges
    by_number = defaultdict(list)
    limit = 5000
    if len(comps) > limit:
        random.shuffle(comps)
        comps = comps[0:limit]
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
        "challenges_config": challenges_config,
        "by_number": by_number,
        "champions": champions_,
        "layout": layout,
    }
    return args


@app.route("/compositions/<route>")
def route_compositions(route):
    try:
        name, key = compositions_names_routes[route]
        comps = compositions[key]
    except:
        return abort(404)

    args = comps_processing(comps)
    args["challenge_name"] = name
    return render_template("compositions.html", **args)


def args_custom_compositions():
    return {
        "roles": enumerate(roles),
        "regions": regions,
        "region": get_default_region(),
        "layout": layout,
    }


@app.route("/custom_compositions/<region>/<summoners_names>")
@limiter.limit("2/minutes")
def route_custom_compositions(region, summoners_names):
    try:
        region = regions_by_abbreviation[region]
    except:
        return redirect("/custom_compositions")

    try:
        summoners_names = summoners_names.split(",")
        if len({name for name in summoners_names if len(name) >= 2}) != 5:
            raise Exception(f"Require five valid distinct summoners name.")
        comps = get_custom_optimized_compositions(
            region["id"], summoners_names)
    except Exception as e:
        args = args_custom_compositions() | {
            "error": e,
        }
        return render_template("custom_compositions.html", **args)

    args = comps_processing(comps)
    args["challenge_name"] = f"Custom composition for '{', '.join(summoners_names)}'"
    return render_template("compositions.html", **args)


@app.route("/custom_compositions")
def route_custom_compositions_wizard():
    args = args_custom_compositions()
    return render_template("custom_compositions.html", **args)


def render_multisearch_search(additional_args={}):
    args = {
        "layout": layout,
        "regions": regions,
        "region": get_default_region()
    } | additional_args
    return render_template("multisearch.html", **args)


@app.route("/multisearch")
def route_multisearch():
    return render_multisearch_search()


@app.route("/multisearch/<region>/<summoners_names_text>")
@limiter.limit("2/minutes")
def route_multisearch_result(region, summoners_names_text):
    try:
        region = regions_by_abbreviation[region]
    except:
        return redirect("/multisearch")

    args = {
        "layout": layout,
    }

    summoner_names = list(dict.fromkeys(summoners_names_text.split(",")))

    try:
        if len(summoner_names) > multisearch_max_size:
            raise Exception(
                f"Too many summoner names (max: {multisearch_max_size})")

        summoners_challenges_info = {}
        for summoner in summoner_names:
            info = get_summoner_challenges_info(region['id'], summoner)
            summoners_challenges_info[info["summoner"]["id"]] = info

        priority_scores = compute_challenges_priority_scores(
            summoners_challenges_info)

        args |= {
            "summoners_challenges_info": summoners_challenges_info,
            "priority_scores": priority_scores,
            "challenges_config": challenges_config,
        }
    except Exception as e:
        return render_multisearch_search({"error": e, "summoners_names": "\n".join(summoner_names)})

    return render_template("multisearch_result.html", **args)


@app.route("/intersection/<challenges_id>")
def route_challenge_intersection(challenges_id):
    if challenges_id == "none":
        response = {
            "intersection": [],
            "challenges_additional_intersection": list()
        }
        for id_, c in challenges_data.items():
            for i, ci in enumerate(c):
                response["challenges_additional_intersection"].append(
                    [f"{id_}:{i}", len(ci["champions"])])
        return json.dumps(response)

    try:
        challenges_id = [s for s in challenges_id.split(",")]
        challenges_champions = []
        for ci in challenges_id:
            split = ci.split(":")
            if len(split) == 1:
                id_, subid = split[0], 0
            elif len(split) == 2:
                id_, subid = split
            id_, subid = int(id_), int(subid)
            champions = challenges_data[id_][subid]["champions"]
            challenges_champions.append(champions)
    except:
        return abort(404)

    u = set.intersection(*challenges_champions)

    response = {
        "intersection": list(u),
        "challenges_additional_intersection": list()
    }

    for id_, c in challenges_data.items():
        for i, ci in enumerate(c):
            s = set(ci["champions"])
            uc = u.intersection(s)
            l = len(uc)
            response["challenges_additional_intersection"].append(
                [f"{id_}:{i}", l])

    return json.dumps(response)


@app.route("/champions_selected/<champions>")
def route_champions_selected(champions=""):
    try:
        comp = set(champions.split(","))
        challenges_info = find_challenges_details(comp)
    except:
        return abort(404)

    return json.dumps(challenges_info)


@app.route("/best_fit_roles/<champions>")
def route_best_fit_roles(champions=""):
    try:
        comp = set(champions.split(","))
        roles = best_fit_roles(set(comp))
    except:
        return abort(404)

    return json.dumps(roles)


@app.route("/faq")
def route_faq():
    args = {
        "layout": layout,
    }
    return render_template("faq.html", **args)


@app.route("/communities")
def route_communities():
    args = {
        "layout": layout,
    }
    try:
        discord_communities, discord_tahm_kench = get_discord_communities()
        args |= {
            "discord_communities": discord_communities,
            "discord_tahm_kench": discord_tahm_kench,
        }
    except ConnectionError as e:
        args |= {
            "error": e
        }

    return render_template("communities.html", **args)


@app.errorhandler(404)
def route_page_not_found(e):
    args = {
        "layout": layout,
    }
    return render_template('404.html', **args), 404


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)

from collections import defaultdict
import json

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

from challenges_tools import compute_challenges_priority_scores
from challenges_tools import get_summoner_challenges_info
from challenges_tools import challenges_groups
from challenges_tools import challenges_data
from challenges_tools import challenges_config
from challenges_tools import find_challenges_details
from challenges_tools import champions
from challenges_tools import champions_alphabetical
from challenges_tools import complete_comp
from challenges_tools import find_challenges
from challenges_tools import get_challenge_from_id

from champions_roles import best_fit_roles

from tk_quotes import RandomQuotes

from communities import get_communities

# create the flask app
app = Flask(__name__, static_url_path="/static")
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 60 * 60
app.secret_key = config["app_secret_key"]

# create the request limiter
limiter = Limiter(app, key_func=get_remote_address)

language = "en_US"
multisearch_max_size = 8

composition_limit = 1500

# load the pre-calculated compositions
compositions = json.load(open("static/compositions.json", "r"))

compositions_names_routes = {}
for key in compositions.keys():
    url = key.replace(" ", "_")
    compositions_names_routes[url] = key

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
        default_region = get_region_from_ip(request.environ.get('HTTP_X_REAL_IP', request.remote_addr))
        session["default_region"] = default_region
    return default_region


@app.route("/")
def main():
    return redirect("/team_builder")

@app.route("/challenges_intersection")
def redirect1():
    return redirect("/team_builder")

@app.route("/challenges_intersection/<region>/<summoner>")
def redirect2(region, summoner):
    return redirect(f"/team_builder/{region}/{summoner}")


def args_team_builder(region, summoner):
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


@app.route("/team_builder")
def route_team_builder():
    args = args_team_builder(get_default_region(), "")
    return render_template("team_builder.html", **args)


@app.route("/team_builder/<region>/<summoner>")
@limiter.limit("6/minutes")
def route_team_builder_summoner(region, summoner):
    try:
        region = regions_by_abbreviation[region]
    except:
        return redirect("/team_builder")
    summoner = summoner.replace("_", " ")
    args = args_team_builder(region, summoner)
    try:
        challenges_info = get_summoner_challenges_info(region["id"], summoner)
        args |= challenges_info
    except Exception as e:
        args["error"] = f"Couldn't find '{summoner}' on {region['abbreviation']}"
    return render_template("team_builder.html", **args)

def comps_processing(comps):
    # limit large challenges
    by_number = defaultdict(list)

    comps.sort(key=lambda l: (-len(l[1]), l[-1], "".join(l[0].values())))
    comps = comps[0:composition_limit]

    champions_available = set()
    for comp, challenges, stupidity_level in comps:
        comp = [comp[role] for role in roles]
        by_number[len(challenges)].append((comp, challenges, stupidity_level))
        champions_available |= set(comp)

    champions_ = {
        c: d for c, d in champions.items()
        if c in champions_available
    }

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
        key = compositions_names_routes[route]
        comps = compositions[key]
    except Exception as e:
        return abort(404)

    args = comps_processing(comps)
    args["challenge_name"] = key
    return render_template("compositions.html", **args)


def args_custom_compositions():
    return {
        "roles": enumerate(roles),
        "regions": regions,
        "region": get_default_region(),
        "layout": layout,
    }


@app.route("/optimize/<route>")
def route_optimize(route):
    # route: id1,id2,id3|champion1,champion2
    query_limit = int(2.5e4)
    try:
        challenges, champions = route.split("&")
        challenges = set(challenges.split(",")) - {""}
        champions = set(champions.split(",")) - {""}

        if len(challenges) + len(champions) <= 0:
            raise Exception("")

        comps = []
        for comp in complete_comp(champions, challenges, limit=query_limit):
            challenges_ = find_challenges(comp)
            roles = best_fit_roles(comp)
            comps.append((roles[0], challenges_, roles[1]))
    except Exception as e:
        return abort(404)

    args = comps_processing(comps)
    args["challenge_name"] = "Compositions optimization"
    args["notices"] = []
    if len(comps) > composition_limit:
        args["notices"].append(f"Showing the best {composition_limit} compositions out of {len(comps)} computed.")
    if len(comps) >= query_limit:
        args["notices"].append(f"BEST EFFORT: The optimization stopped early, which means that the current result may be not optimal for the given constraints. To avoid this, be more specific and add more challenges or champions")
    args["constraints"] = []

    for challenge_id in challenges:
        challenge = get_challenge_from_id(challenge_id)
        challenge = challenges_config[challenge['id']]
        args["constraints"].append(challenge["localizedNames"][language]["name"])
    for champion in champions:
        args["constraints"].append(champion)

    return render_template("compositions.html", **args)


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
            challenge = get_challenge_from_id(ci)
            champions = challenge["champions"]
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
        communities = get_communities()
        args |= {
            "communities": communities,
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

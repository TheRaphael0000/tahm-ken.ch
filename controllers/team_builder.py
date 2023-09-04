import json

from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import abort

from models.challenges_tools import champions
from models.challenges_tools import champions_alphabetical
from models.challenges_tools import challenges_data
from models.challenges_tools import challenges_groups
from models.challenges_tools import challenges_config
from models.challenges_tools import get_summoner_challenges_info
from models.challenges_tools import get_challenge_from_id
from models.challenges_tools import find_challenges_details

from models.champions_roles import best_fit_roles

from models.regions import regions
from models.regions import regions_by_abbreviation

from global_data import layout
from global_data import get_default_region


bp_team_builder = Blueprint(
    'bp_team_builder', __name__, template_folder='templates')


@bp_team_builder.route("/")
def main():
    return redirect("/team_builder")


@bp_team_builder.route("/challenges_intersection")
def redirect1():
    return redirect("/team_builder")


@bp_team_builder.route("/challenges_intersection/<region>/<summoner>")
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


@bp_team_builder.route("/team_builder")
def route_team_builder():
    args = args_team_builder(get_default_region(), "")
    try:
        result = render_template("team_builder.html", **args)
    except Exception as e:
        raise e
        return abort(404)
    return result


@bp_team_builder.route("/team_builder/<region>/<summoner>")
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


@bp_team_builder.route("/intersection/<challenges_id>")
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


@bp_team_builder.route("/champions_selected/<champions>")
def route_champions_selected(champions=""):
    try:
        comp = set(champions.split(","))
        challenges_info = find_challenges_details(comp)
    except:
        return abort(404)

    return json.dumps(challenges_info)


@bp_team_builder.route("/best_fit_roles/<champions>")
def route_best_fit_roles(champions=""):
    try:
        comp = set(champions.split(","))
        roles = best_fit_roles(set(comp))
    except:
        return abort(404)

    return json.dumps(roles)

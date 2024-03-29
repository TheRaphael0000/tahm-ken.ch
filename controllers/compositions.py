from flask import render_template
from flask import Blueprint
from flask import abort

from collections import defaultdict

from models.challenges_tools import champions
from models.challenges_tools import challenges_config
from models.challenges_tools import complete_comp
from models.challenges_tools import find_challenges
from models.challenges_tools import get_challenge_from_id

from models.compositions import compositions
from models.compositions import compositions_names_routes
from global_data import layout
from global_data import language

from models.champions_positions import best_fit_positions
from models.champions_positions import X_label as positions

composition_limit = 1500
query_limit = 25000

bp_compositions = Blueprint(
    'compositions', __name__, template_folder='templates')


def comps_processing(comps):
    # limit large challenges
    by_number = defaultdict(list)

    comps.sort(key=lambda l: (-len(l[1]), -l[-1], "".join(l[0].values())))
    comps = comps[0:composition_limit]

    champions_available = set()
    for comp, challenges, attribution_score in comps:
        comp = [comp[position] for position in positions]
        by_number[len(challenges)].append(
            (comp, challenges, attribution_score))
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


@bp_compositions.route("/compositions/<route>")
def route_compositions(route):
    try:
        key = compositions_names_routes[route]
        comps = compositions[key]
    except Exception as e:
        return abort(404)

    args = comps_processing(comps)
    args["challenge_name"] = key
    return render_template("compositions.html", **args)


@bp_compositions.route("/optimize/<route>")
def route_optimize(route):
    # route: id1,id2,id3|champion1,champion2
    try:
        challenges, champions = route.split("&")
        challenges = set(challenges.split(",")) - {""}
        champions = set(champions.split(",")) - {""}

        if len(challenges) + len(champions) <= 0:
            raise Exception("")

        comps = []
        for comp in complete_comp(champions, challenges, limit=query_limit):
            challenges_ = find_challenges(comp)
            roles = best_fit_positions(comp)
            comps.append((roles[0], challenges_, roles[1]))
    except Exception as e:
        return abort(404)

    args = comps_processing(comps)
    args["challenge_name"] = "Compositions optimization"
    args["notices"] = []
    if len(comps) > composition_limit:
        args["notices"].append(
            f"Showing the best {composition_limit} compositions out of {len(comps)} computed.")
    if len(comps) >= query_limit:
        args["notices"].append(
            f"BEST EFFORT: The optimization stopped early, which means that the current result may be not optimal for the given constraints. To avoid this, be more specific and add more challenges or champions")
    args["constraints"] = []

    for challenge_id in challenges:
        challenge = get_challenge_from_id(challenge_id)
        challenge = challenges_config[challenge['id']]
        args["constraints"].append(
            challenge["localizedNames"][language]["name"])
    for champion in champions:
        args["constraints"].append(champion)

    return render_template("compositions.html", **args)

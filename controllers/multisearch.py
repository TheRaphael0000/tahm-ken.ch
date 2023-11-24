from flask import Blueprint
from flask import render_template
from flask import redirect

from models.regions import regions
from models.regions import regions_by_abbreviation

from global_data import layout
from global_data import get_default_region

from models.challenges_tools import get_summoner_challenges_info
from models.challenges_tools import compute_challenges_priority_scores
from models.challenges_tools import challenges_config
from models.challenges_tools import challenges_data

bp_multisearch = Blueprint('bp_multisearch', __name__,
                           template_folder='templates')
multisearch_max_size = 8


def render_multisearch_search(additional_args={}):
    args = {
        "layout": layout,
        "regions": regions,
        "region": get_default_region()
    } | additional_args
    return render_template("multisearch.html", **args)


@bp_multisearch.route("/multisearch")
def route_multisearch():
    return render_multisearch_search()


@bp_multisearch.route("/multisearch/<region>/<summoners_names_text>")
def route_multisearch_result(region, summoners_names_text):
    try:
        region = regions_by_abbreviation[region]
    except:
        return redirect("/multisearch")

    args = {
        "layout": layout,
    }

    queries = list(dict.fromkeys(summoners_names_text.split(",")))

    try:
        if len(queries) > multisearch_max_size:
            raise Exception(
                f"Too many summoner names (max: {multisearch_max_size})")

        summoners_challenges_info = {}
        for query in queries:
            print(query)
            info = get_summoner_challenges_info(region['id'], query)
            summoners_challenges_info[info["summoner"]["id"]] = info

        priority_scores = compute_challenges_priority_scores(
            summoners_challenges_info)

        args |= {
            "summoners_challenges_info": summoners_challenges_info,
            "priority_scores": priority_scores,
            "challenges_config": challenges_config,
            "challenges_data": challenges_data,
        }
    except Exception as e:
        return render_multisearch_search({"error": e, "summoners_names": "\n".join(queries)})

    return render_template("multisearch_result.html", **args)

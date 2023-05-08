from flask import render_template
from flask import Blueprint

from global_data import layout

from models.communities import get_communities


bp_communities = Blueprint('communities', __name__,
                           template_folder='templates')


@bp_communities.route("/communities")
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

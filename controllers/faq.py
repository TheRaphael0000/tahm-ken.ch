from flask import render_template
from flask import Blueprint

from global_data import layout

bp_faq = Blueprint('faq', __name__, template_folder='templates')


@bp_faq.route("/faq")
def route_faq():
    args = {
        "layout": layout,
    }
    return render_template("faq.html", **args)

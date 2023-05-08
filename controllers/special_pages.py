from flask import render_template
from flask import Blueprint

from global_data import layout

bp_special_pages = Blueprint(
    'bp_special_pages', __name__, template_folder='templates')


@bp_special_pages.app_errorhandler(404)
def route_page_not_found(e):
    args = {
        "layout": layout,
    }
    return render_template('404.html', **args), 404

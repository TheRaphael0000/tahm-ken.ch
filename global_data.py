from flask import session
from flask import request

from models.quotes import random_quote
from models.regions import get_region_from_ip
from models.compositions import compositions_names_routes


language = "en_US"


# variables which are required for the layout
layout = {
    "quote": random_quote,
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

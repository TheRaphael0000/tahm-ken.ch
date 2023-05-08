from flask import session

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

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

limiter = Limiter(get_remote_address)


def get_default_region():
    # store the region in the session
    # to avoid having to lookup multiple times
    if "default_region" in session:
        default_region = session["default_region"]
    else:
        default_region = get_region_from_ip(get_remote_address())
        session["default_region"] = default_region
    return default_region

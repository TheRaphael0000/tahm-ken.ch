from flask import Flask

from config import config

from controllers.multisearch import bp_multisearch
from controllers.team_builder import bp_team_builder
from controllers.compositions import bp_compositions
from controllers.faq import bp_faq
from controllers.communities import bp_communities
from controllers.special_pages import bp_special_pages

# create the flask app
app = Flask(__name__, static_url_path="/static")
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 60 * 60
app.secret_key = config["app_secret_key"]

app.register_blueprint(bp_multisearch)
app.register_blueprint(bp_team_builder)
app.register_blueprint(bp_compositions)
app.register_blueprint(bp_faq)
app.register_blueprint(bp_communities)
app.register_blueprint(bp_special_pages)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)

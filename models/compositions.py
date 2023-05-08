import json

# load the pre-calculated compositions
compositions = json.load(open("static/compositions.json", "r"))

compositions_names_routes = {}
for key in compositions.keys():
    url = key.replace(" ", "_")
    compositions_names_routes[url] = key

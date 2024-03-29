import requests
import json


def save(url, path):
    print(f"{url} -> {path}")
    data = requests.get(url).json()
    json.dump(data, open(path, "w"))


save("https://lol-web-api.op.gg/api/v1.0/internal/bypass/champions/euw/ranked",
     "static/cache_opgg/champions_ranked.json")

import requests
import json
from pathlib import Path


def save():
    url = "https://lol-web-api.op.gg/api/v1.0/internal/bypass/champions/euw/ranked"
    path = Path("static/cache/opgg")
    print(f"{url} -> {path}")
    data = requests.get(url).json()
    path.mkdir(parents=True, exist_ok=True)
    json.dump(data, open(path / "champions_ranked.json", "w"))


save()

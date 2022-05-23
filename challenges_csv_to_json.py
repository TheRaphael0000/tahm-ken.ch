"""
Convert the csv file into a json
"""

import itertools
import pandas
import pprint
import json

df = pandas.read_csv("challenges.csv")

challenges = []

for challenge_name in list(df)[1:]:
    indices = df[df[challenge_name] == "1"].index
    champions = df["Champion"][indices]
    challenge_name_fr = df[challenge_name][0]
    qte = df[challenge_name][1]

    data = {
    "challenge_name" : challenge_name,
    "challenge_name_fr" : challenge_name_fr,
    "champions" : tuple(champions),
    "qte" : qte
    }

    challenges.append(data)

pprint.pprint(challenges)
json.dump(challenges, open("challenges.json", "w"), indent=4, sort_keys=False)

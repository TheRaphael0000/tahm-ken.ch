from collections import defaultdict
import itertools
import json
import sys

import numpy as np
import matplotlib.pyplot as plt
from riotwatcher import LolWatcher
from riotwatcher import ApiError

from config import config
from constants import default_region

challenges = json.load(open("static/challenges.json"))
for c in challenges:
    c["champions_l"] = len(c["champions"])
challenges.sort(key=lambda l: -l["champions_l"])
challenges.sort(key=lambda l: l["qte"])

for c in challenges:
    c["champions"] = set(c["champions"])
    c["qte"] = c["qte"]


challenges_by_champions = defaultdict(list)
for challenge in challenges:
    for champion in challenge["champions"]:
        challenges_by_champions[champion].append(challenge["challenge_name"])
challenges_by_champions = dict(challenges_by_champions)

champions_by_challenge = {}
for challenge in challenges:
    champions_by_challenge[
        challenge["challenge_name"]
    ] = challenge["champions"]


# load champions data
champions = json.load(
    open("static/datadragon_cache/champion.json", "rb"))["data"]
champions_keys = sorted(champions, key=lambda c: champions[c]["name"])
champions_by_keys = {int(champion["key"]):champion for _, champion in champions.items()}

try:
    lol_watcher = None
    challenges_config = None
    lol_watcher = LolWatcher(config["riot_api_key"])
    challenges_config = lol_watcher.challenges.config(default_region)
    challenges_config = {c["id"]: c for c in challenges_config}
    # add the challenges data from the riot api to the json data
    for challenge in challenges:
        challenge["config"] = challenges_config[challenge["riot_id"]]
except ValueError:
    print("No Riot API key provided")
except ApiError:
    print("This Riot API key can't access the challenges scope")


def find_challenges(comp):
    challenges_achieved = set()
    for c in challenges:
        if len(c["champions"].intersection(comp)) >= c["qte"]:
            challenges_achieved.add(c["challenge_name"])
    return challenges_achieved


def find_comp(champions_, threshold_min=0, threshold_max=sys.maxsize, max_depth=1e7):
    # sort them by number of challenges to find good match first
    champions_ = list(champions_)
    champions_.sort(key=lambda c: -len(challenges_by_champions[c]))

    # iterate over all champion combinations
    i = 0
    for comp in itertools.combinations(champions_, 5):
        comp_challenges = find_challenges(set(comp))
        if threshold_min <= len(comp_challenges) <= threshold_max:
            yield comp, comp_challenges

        if i > max_depth:
            return
        i += 1


def find_comp_randomly(champions, p, max_depth=1e8):
    for i in range(int(max_depth)):
        values = np.random.choice(
            np.array(range(len(champions))), size=5, replace=False, p=p)
        comp = [champions[v] for v in values]
        comp_challenges = find_challenges(set(comp))
        yield comp, comp_challenges


def find_comp_randomly_team(data, max_depth=1e8):
    for i in range(int(max_depth)):
        comp = list()
        for champions_, pi in data:
            champions_copy = list(champions_)
            pi_copy = np.array(pi)
            for c in comp:
                i = champions_copy.index(c)
                pi_copy = np.delete(pi_copy, i)
                champions_copy.remove(c)
                pi_copy /= pi_copy.sum()

            ids = np.array(range(len(champions_copy)))
            id_ = np.random.choice(ids, p=pi_copy)
            comp.append(champions_copy[id_])
        comp_challenges = find_challenges(set(comp))
        yield comp, comp_challenges


def champions_probability_table(power=1, alpha=1):
    champions = list(challenges_by_champions.keys())
    p = np.array([len(challenges_by_champions[champion])
                 ** power for champion in champions])
    if alpha > 0:
        p += alpha
    p = p/p.sum()
    return champions, p


def plot_champion_distribution(x, y):
    x_y = list(zip(x, y))
    x_y.sort(key=lambda l: -l[-1])
    x, y = zip(*x_y)

    plt.figure(figsize=(100, 5))
    y_pos = np.arange(len(x))
    plt.bar(y_pos, y, align='center', alpha=0.5)
    plt.xticks(y_pos, x)
    plt.show()


def get_custom_optimized_compositions(region, summoners_names, power=1.3, max_depth=1e4):
    # check if summoners exist
    summoners = []
    for summoner_name in summoners_names:
        try:
            summoner = lol_watcher.summoner.by_name(
                region=region, summoner_name=summoner_name)
            summoners.append(summoner)
        except ApiError as err:
            if err.response.status_code == 404:
                raise Exception(f"{summoner_name} doesn't exist !")
            else:
                raise Exception("Unhandled error")

    data = []
    for summoner in summoners:
        summoner_masteries = lol_watcher.champion_mastery.by_summoner(
            region=region, encrypted_summoner_id=summoner["id"])

        masteries_by_id = {mastery["championId"]                           : mastery for mastery in summoner_masteries}
        champion_masteries = {}

        for champion_id, champion in champions.items():
            champion_key = int(champion["key"])
            if champion_key not in masteries_by_id:
                champion_masteries[champion_id] = 0
            else:
                champion_masteries[champion_id] = masteries_by_id[champion_key]["championPoints"] ** power

        champions_ = list(champion_masteries.keys())
        p = np.array(list(champion_masteries.values()))
        p = p/p.sum()

        data.append((champions_, p))

    comp_found = set()
    comps_ = []

    for comp, comp_challenges in find_comp_randomly_team(data, max_depth=max_depth):
        if len(comp_challenges) < 3:
            continue

        comp_str = str(sorted(list(comp)))
        if comp_str not in comp_found:
            comp_found.add(comp_str)
            comps_.append((comp, list(comp_challenges)))

    return comps_

def get_summoner_challenges_infos(region, summoner):
    summoner = lol_watcher.summoner.by_name(region, summoner)
    summoner_challenges_infos = lol_watcher.challenges.by_puuid(
        region, summoner['puuid'])

    summoner_challenges_by_id = {
        c["challengeId"]: c for c in summoner_challenges_infos["challenges"]}

    challenges_for_this_summoner = {}
    for c in challenges:
        id_ = c["riot_id"]

        challenge_for_this_summoner = {
            "level": "unranked",
            "value": 0,
        }

        if id_ in summoner_challenges_by_id:
            challenge_for_this_summoner = {
                "level": summoner_challenges_by_id[id_]["level"].lower(),
                "value": int(summoner_challenges_by_id[id_]["value"]),
            }

        # get the next threshold to upgrade the challenge
        thresholds = list(c["config"]["thresholds"].items())
        thresholds.sort(key=lambda l: l[-1])
        next_threshold = None
        if challenge_for_this_summoner["level"] not in ["MASTER", "GRANDMASTER", "CHALLENGER"]:
            for _, threshold in thresholds:
                if threshold > challenge_for_this_summoner["value"]:
                    next_threshold = str(int(threshold))
                    break

        challenge_for_this_summoner["next_threshold"] = next_threshold

        challenges_for_this_summoner[id_] = challenge_for_this_summoner
    
    total_points = summoner_challenges_infos["totalPoints"]
    
    # avoid having no crystal for 0 points accounts
    if total_points["level"] == "NONE":
        total_points["level"] = "IRON"

    return challenges_for_this_summoner, total_points
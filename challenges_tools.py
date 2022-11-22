from collections import defaultdict
import itertools
import json
import sys
import random

import scipy as sp
import numpy as np
import matplotlib.pyplot as plt
from riotwatcher import LolWatcher
from riotwatcher import ApiError

from config import config
from regions import default_region
from constants import roles

from champions_roles import best_fit_roles
from champions_roles import champions
from champions_roles import champions_by_roles

challenges_groups = [
    {
        "parent": 303400,
        "children": [
            303401,
            303402,
            303403,
            303404,
            303405,
            303406,
            303407,
            303408,
            303409,
            303410,
            303411,
            303412,
        ],
    },
    {
        "parent": 303500,
        "children": [
            303501,
            303502,
            303503,
            303504,
            303505,
            303506,
            303507,
            303508,
            303509,
            303510,
            303511,
            303512,
            303513,
        ],
    },
]


challenges_data = json.load(open("static/challenges.json"))
for c in challenges_data:
    c["max"] = len(c["champions"])
    c["champions"] = set(c["champions"])


challenges_by_champions = defaultdict(list)
for challenge in challenges_data:
    for champion in challenge["champions"]:
        challenges_by_champions[champion].append(challenge["id"])
challenges_by_champions = dict(challenges_by_champions)

champions_by_challenge = {
    challenge["id"]: challenge["champions"]
    for challenge in challenges_data
}

# load champions data
champions_alphabetical = sorted(champions, key=lambda c: champions[c]["name"])

try:
    lol_watcher = None
    challenges_config = None
    lol_watcher = LolWatcher(config["riot_api_key"])
    # the region doesn't matter
    challenges_config = lol_watcher.challenges.config(default_region)
    challenges_config = {c["id"]: c for c in challenges_config}
    for c in challenges_data:
        challenges_config[c['id']]["qte"] = c["qte"]
        challenges_config[c['id']]["max"] = c["max"]
except ValueError:
    print("No Riot API key provided")
except ApiError:
    print("This Riot API key can't access the challenges scope")


challenges_data_ = defaultdict(list)
for c in challenges_data:
    challenges_data_[c["id"]].append(c)
challenges_data = dict(challenges_data_)


def find_challenges(comp):
    challenges_achieved = set()
    for id_, challenge in challenges_data.items():
        for c in challenge:
            if len(c["champions"].intersection(comp)) >= c["qte"]:
                challenges_achieved.add(c["id"])
    return challenges_achieved


def find_challenges_details(comp):
    challenges_details = {}
    for id_, challenge in challenges_data.items():
        for c in challenge:
            current = list(set(comp).intersection(set(c["champions"])))
            if id_ not in challenges_details or len(current) > len(challenges_details[id_]):
                challenges_details[id_] = current
    return challenges_details


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
                if c in champions_copy:
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
    for summoner, role in zip(summoners, roles):
        summoner_masteries = lol_watcher.champion_mastery.by_summoner(
            region=region, encrypted_summoner_id=summoner["id"])

        masteries_by_id = {mastery["championId"]
            : mastery for mastery in summoner_masteries}
        champion_masteries = {}

        for champion_id, champion in champions.items():
            champion_key = int(champion["key"])
            if champion_key not in masteries_by_id:
                champion_masteries[champion_id] = 0
            else:
                champion_masteries[champion_id] = masteries_by_id[champion_key]["championPoints"] ** power

        filter_champion_by_role = {}
        for k, v in champion_masteries.items():
            if k in champions_by_roles[role]:
                filter_champion_by_role[k] = v

        champions_ = list(filter_champion_by_role.keys())
        p = np.array(list(filter_champion_by_role.values()))
        p = p/p.sum()

        data.append((champions_, p))

    comp_found = set()
    comps_ = []

    for comp, comp_challenges in find_comp_randomly_team(data, max_depth=max_depth):
        if len(comp_challenges) < 3:
            continue

        comp_roles, stupidity_level, off_role = best_fit_roles(comp)

        comp_str = str(sorted(list(comp)))
        if comp_str not in comp_found:
            comp_found.add(comp_str)
            comps_.append((comp_roles, list(comp_challenges), stupidity_level))

    return comps_


def get_summoner_challenges_info(region, summoner):
    try:
        summoner = lol_watcher.summoner.by_name(region, summoner)
    except:
        raise Exception(f"{summoner} not found on {region}")
    summoner_challenges_infos = lol_watcher.challenges.by_puuid(
        region, summoner['puuid'])

    summoner_challenges_by_id = {
        c["challengeId"]: c for c in summoner_challenges_infos["challenges"]}

    def find_next_threshold(thresholds, challenge_for_this_summoner):
        if challenge_for_this_summoner["level"] in ["master", "grandmaster", "challenger"]:
            return None

        thresholds = list(thresholds.items())
        thresholds.sort(key=lambda l: l[-1])

        for _, threshold in thresholds:
            if threshold > challenge_for_this_summoner["value"]:
                return str(int(threshold))

    def create_summoner_challenge(challenge_id):
        if challenge_id in summoner_challenges_by_id:
            challenge_for_this_summoner = {
                "level": summoner_challenges_by_id[challenge_id]["level"].lower(),
                "value": int(summoner_challenges_by_id[challenge_id]["value"]),
            }
        else:
            challenge_for_this_summoner = {
                "level": "iron",
                "value": 0,
            }

        challenge_for_this_summoner["next_threshold"] = find_next_threshold(
            challenges_config[challenge_id]["thresholds"], challenge_for_this_summoner)
        return challenge_for_this_summoner

    summoner_challenges = {
        challenge_id: create_summoner_challenge(challenge_id)
        for challenge_id in challenges_data.keys()
    }

    total_points = summoner_challenges_infos["totalPoints"]
    total_points["level"] = total_points["level"].lower()

    # avoid having no crystal for 0 points accounts
    if total_points["level"] == "none":
        total_points["level"] = "iron"

    return {"summoner": summoner, "summoner_challenges": summoner_challenges, "total_points": total_points}


def compute_challenges_priority_scores(challenges_info):
    priority_scores = defaultdict(lambda: 1)
    # compute geometric mean
    for sid_, s in challenges_info.items():
        for id_, challenge in s["summoner_challenges"].items():
            # +1: avoid having to multiply by 0
            # min: avoid having too high progress having too much influence
            # +5: more margin for the min
            priority_scores[id_] *= min(challenge["value"] + 1,
                                        challenges_config[id_]["thresholds"]["MASTER"] + 5)

    N = len(challenges_info)
    # take the square root
    for id_ in priority_scores:
        priority_scores[id_] **= 1/N

    # range the values
    min_, max_ = min(priority_scores.values()), max(priority_scores.values())
    min_range, max_range = 1, 100
    for id_, score in priority_scores.items():
        score = (score - min_) / (max_ - min_)
        score = score * (max_range - min_range) + min_range
        priority_scores[id_] = score

    # sort the array
    priority_scores = list(priority_scores.items())
    priority_scores.sort(key=lambda l: l[-1])

    return priority_scores


def complete_comp_(selected_champions, selected_challenges):
    champions_ = [*challenges_by_champions]
    comp_size = 5
    # print("enter", selected_champions, selected_challenges)

    if len(selected_champions) >= comp_size and len(selected_challenges) <= 0:
        # print("select", selected_champions)
        yield selected_champions

    challenges_to_explore = []
    total_missing = comp_size - len(selected_champions)
    remaining_champions = set(champions_).difference(selected_champions)

    # add each selected challenge exploration range
    det = find_challenges_details(selected_champions)
    for challenge_id in selected_challenges:
        challenge = challenges_data[challenge_id][0]
        l = {}
        l["challenge_id"] = challenge_id
        l["addable_champions"] = challenge["champions"] - selected_champions
        l["missing"] = challenge["qte"] - len(det[challenge_id])
        l["missing"] = max(l["missing"], 0)
        l["size"] = len(l["addable_champions"])
        l["explore_size"] = sp.special.comb(l["size"], l["missing"])
        challenges_to_explore.append(l)

    challenges_to_explore.sort(key=lambda l: l["explore_size"])

    # add the missing champions in case default
    challenges_to_explore.append({
        "challenge_id": None,
        "addable_champions": set(remaining_champions) - selected_champions,
        "missing": total_missing,
        "size": len(remaining_champions),
        "explore_size": sp.special.comb(len(remaining_champions), total_missing)
    })

    # pick the most easy to explore first
    challenge_to_explore = challenges_to_explore[0]
    max_missing = max([i["missing"] for i in challenges_to_explore])

    # print("explore", [(i["challenge_id"], i["missing"], i["size"], i["explore_size"]) for i in challenges_to_explore])

    # this branch is impossible
    if max_missing > total_missing or challenge_to_explore["size"] < total_missing:
        # print("none", selected_champions, selected_challenges)
        yield None

    addable_champions = list(challenge_to_explore["addable_champions"])
    random.shuffle(addable_champions)

    for additional_champions in itertools.combinations(addable_champions, challenge_to_explore["missing"]):
        new_selected_champions = selected_champions | set(additional_champions)
        remaining_challenges = selected_challenges - {challenge_to_explore["challenge_id"]}
        if len(new_selected_champions) >= comp_size and len(remaining_challenges) <= 0:
            yield new_selected_champions
            continue

        for comp in complete_comp(new_selected_champions, remaining_challenges):
            if comp is None:
                break
            else:
                yield comp


def complete_comp(selected_champions, selected_challenges, limit=1e5):
    count = 0
    for i in complete_comp_(selected_champions, selected_challenges):
        if i is None:
            break
        if count >= limit:
            break
        count += 1
        yield i
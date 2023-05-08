from collections import defaultdict
import itertools
import json
from pprint import pprint

import scipy as sp
import scipy.special
from riotwatcher import LolWatcher
from riotwatcher import ApiError
from engineering_notation import EngNumber

from config import config
from models.regions import default_region

from models.champions_roles import champions

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

champions_by_key = {champion["key"]
    : champion for id_, champion in champions.items()}

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

    progress = 0
    total = 0
    summoner_challenges = {}

    for challenge_id in challenges_data.keys():
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

        thresholds = challenges_config[challenge_id]["thresholds"]
        challenge_for_this_summoner["next_threshold"] = find_next_threshold(
            thresholds, challenge_for_this_summoner)
        summoner_challenges[challenge_id] = challenge_for_this_summoner

        threshold_MASTER = thresholds["MASTER"]
        progress += min(challenge_for_this_summoner["value"], threshold_MASTER)
        total += threshold_MASTER

    total_points = summoner_challenges_infos["totalPoints"]
    total_points["level"] = total_points["level"].lower()

    # avoid having no crystal for 0 points accounts
    if total_points["level"] == "none":
        total_points["level"] = "iron"

    champion_masteries = get_champion_mastery_by_challenge(
        region, summoner['id'])

    output = {
        "summoner": summoner,
        "summoner_challenges": summoner_challenges,
        "total_points": total_points,
        "progress": progress,
        "total": total,
        "progress_ratio": progress / total,
        "champion_masteries": champion_masteries,
    }

    return output


def get_champion_mastery_by_challenge(region, summoner_puuid):
    champions_masteries = lol_watcher.champion_mastery.by_summoner(
        region, summoner_puuid)
    for cm in champions_masteries:
        cm["championPointsE"] = str(
            EngNumber(cm["championPoints"], precision=0))
        cm["championId"] = champions_by_key[str(cm["championId"])]["id"]
    champions_masteries_by_id = {
        c["championId"]: c for c in champions_masteries}
    summoner_played_champions = set(champions_masteries_by_id.keys())

    champion_mastery_by_challenge = {}
    for challenge_id, subchallenges in challenges_data.items():
        challenge_champions = set.union(
            *[subchallenge["champions"] for subchallenge in subchallenges])
        challenge_champions_key_played = summoner_played_champions.intersection(
            challenge_champions)
        challenge_champions_masteries = [
            champions_masteries_by_id[c] for c in challenge_champions_key_played]
        challenge_champions_masteries.sort(key=lambda l: -l["championPoints"])
        champion_mastery_by_challenge[challenge_id] = challenge_champions_masteries

    return champion_mastery_by_challenge


def compute_challenges_priority_scores(challenges_info):
    is_max_scores = defaultdict(lambda: 0)
    progress_error = defaultdict(lambda: 0)

    for sid_, s in challenges_info.items():
        for id_, challenge in s["summoner_challenges"].items():
            # completion
            is_maxed = challenge["next_threshold"] is None
            is_max_scores[id_] += 1 if is_maxed else 0
            # progress
            max_step = challenges_config[id_]["thresholds"]["MASTER"]
            error = abs(max_step - min(challenge["value"], max_step))
            progress_error[id_] += error

    N = len(challenges_info)
    # take the square root
    for id_ in progress_error:
        progress_error[id_] /= N

    ids = set(progress_error) & set(is_max_scores)
    priority_scores = [(id_, is_max_scores[id_], progress_error[id_])
                       for id_ in ids]

    # sort the array
    priority_scores.sort(key=lambda l: (l[1], -l[2], l[0]))
    return priority_scores


def get_challenge_from_id(challenge_id):
    challenge_id_split = challenge_id.split(":")
    id_ = int(challenge_id_split[0])
    try:
        sub_id_ = int(challenge_id_split[1])
    except:
        sub_id_ = 0
    challenge = challenges_data[id_][sub_id_]
    return challenge


def complete_comp_(selected_champions, selected_challenges):
    champions_ = [*challenges_by_champions]
    comp_size = 5

    if len(selected_champions) >= comp_size and len(selected_challenges) <= 0:
        yield selected_champions

    challenges_to_explore = []
    total_missing = comp_size - len(selected_champions)
    remaining_champions = set(champions_).difference(selected_champions)

    # add each selected challenge exploration range
    det = find_challenges_details(selected_champions)
    for challenge_id in selected_challenges:
        challenge = get_challenge_from_id(challenge_id)
        l = {
            "challenge_id": challenge_id,
            "addable_champions": challenge["champions"] - selected_champions,
            "missing": max(challenge["qte"] - len(det[challenge["id"]]), 0)
        }
        l["size"] = len(l["addable_champions"])
        l["explore_size"] = scipy.special.comb(l["size"], l["missing"])
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

    # this branch is impossible
    if max_missing > total_missing or challenge_to_explore["size"] < total_missing:
        yield None

    addable_champions = list(challenge_to_explore["addable_champions"])
    addable_champions.sort(key=lambda l: (-len(challenges_by_champions[l]), l))

    for additional_champions in itertools.combinations(addable_champions, challenge_to_explore["missing"]):
        new_selected_champions = selected_champions | set(additional_champions)
        remaining_challenges = selected_challenges - \
            {challenge_to_explore["challenge_id"]}
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

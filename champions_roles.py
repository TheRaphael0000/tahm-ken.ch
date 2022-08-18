from collections import defaultdict
import random
import json
import re

champions = json.load(
    open("static/datadragon_cache/champion.json", "rb"))["data"]


filedata = open("static/txt/champions_roles.csv").read()

champions_by_ig_name = {champion["name"]: champion for _, champion in champions.items()}

lines = filedata.split("\n")

roles = set()
infos_by_champions = defaultdict(dict)

for line in lines[1:]:
    data = line.split(",")
    if len(data) < 6:
        continue
    champion, role, _, _, pick_rate, _ = data[0:6]
    champion = champions_by_ig_name[champion]["id"]
    infos_by_champions[champion][role] = float(pick_rate[0:-1])
    roles.add(role)


champions_roles_pickrate = []
for champion, roles_ in infos_by_champions.items():
    for role in roles_:
        pick_rate = infos_by_champions[champion][role]
        champions_roles_pickrate.append((champion, role, pick_rate))
champions_roles_pickrate.sort(key=lambda l: -l[-1])

# create champion and role lookup from the pick rate
# to priorities these champions for certain roles with the best fit
champions_by_roles = defaultdict(list)
roles_by_champions = defaultdict(list)
for champion, role, pick_rate in champions_roles_pickrate:
    champions_by_roles[role].append(champion)
    roles_by_champions[champion].append(role)


def best_fit_roles(comp):
    comp = list(comp)
    comp_roles = {}
    stupidity_level = 0

    # input checks
    if len(set(comp)) != 5:
        raise Exception("Need 5 distinct champions")

    for champion in comp:
        if champion not in infos_by_champions:
            raise Exception(f"Invalid champion provided : {champion}")

    # create a priority queue with both direction
    # this find which role is most needed or which champion mostly need a role
    # in order of priority
    def create_priority_queue(comp_, remaining_roles):
        priority_queue = []
        for champion in comp_:
            role4champion = [
                role for role in roles_by_champions[champion] if role in remaining_roles]
            if len(role4champion) > 0:
                priority_queue.append(
                    ("role4champion", role4champion, champion))

        for remaining_role in remaining_roles:
            champions4role = [
                champion for champion in champions_by_roles[remaining_role] if champion in comp_]
            if len(champions4role) > 0:
                priority_queue.append(
                    ("champion4role", champions4role, remaining_role))

        priority_queue.sort(key=lambda l: len(l[1]))

        return priority_queue

    # maximal iteration is 5
    for _ in range(5):
        remaining_roles = {role for role in roles if role not in comp_roles}
        priority_queue = create_priority_queue(comp, remaining_roles)

        # end early if its a stupid comp
        if len(priority_queue) <= 0:
            break

        order, data1, data2 = priority_queue[0]

        if order == "role4champion":
            selected_champion = data2
            selected_role = data1[0]
        elif order == "champion4role":
            selected_champion = data1[0]
            selected_role = data2

        comp_roles[selected_role] = selected_champion
        comp.remove(selected_champion)

    # complete the comp by adding randomly the champion at some role
    for role in roles:
        if role not in comp_roles:
            stupidity_level += 1
            selected_champion = random.choice(comp)
            comp_roles[role] = selected_champion
            comp.remove(selected_champion)

    return comp_roles, stupidity_level


if __name__ == "__main__":
    print(best_fit_roles(["Singed", "Tristana", "Lux", "Zoe", "Poppy"]))
    print(best_fit_roles(["Pantheon", "Zac", "Lux", "Kaisa", "Urgot"]))
    print(best_fit_roles(
        ["Pantheon", "Zac", "Singed", "Tryndamere", "Karthus"]))
    print(best_fit_roles(["Singed", "Lux", "Lux", "Zoe", "Poppy"]))

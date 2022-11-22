from collections import defaultdict
import random
import json

champions = json.load(
    open("static/datadragon_cache/champion.json", "rb"))["data"]


champions_by_roles = json.load(open("static/champions_roles.json", "r"))

champions_by_ig_name = {
    champion["name"]: champion
    for _, champion in champions.items()
}

roles = {*champions_by_roles}
roles_by_champions = defaultdict(list)
for role, champions_ in champions_by_roles.items():
    for champion in champions_:
        roles_by_champions[champion].append(role)
roles_by_champions = dict(roles_by_champions)


def best_fit_roles(comp):
    comp = list(comp)
    comp_roles = {}
    off_role = []

    # input checks
    if len(set(comp)) != 5:
        raise Exception("Need 5 distinct champions")

    for champion in comp:
        if champion not in roles_by_champions:
            raise Exception(f"Invalid champion provided : {champion}")

    # create a priority queue with both direction
    # this find which role is most needed or which champion mostly need a role
    # in order of priority
    def create_priority_queue(comp_, remaining_roles):
        priority_queue = []
        for champion in comp_:
            role4champion = [
                role for role in roles_by_champions[champion]
                if role in remaining_roles
            ]
            if len(role4champion) > 0:
                priority_queue.append(
                    ("role4champion", role4champion, champion))

        for remaining_role in remaining_roles:
            champions4role = [
                champion for champion in champions_by_roles[remaining_role]
                if champion in comp_
            ]
            if len(champions4role) > 0:
                priority_queue.append(
                    ("champion4role", champions4role, remaining_role))

        def sort_key(l):
            order, data1, data2 = l
            s1 = len(l[1])
            s2 = 9000
            if order == "role4champion" and len(data1) == 1:
                s2 = champions_by_roles[data1[0]].index(data2)
            if order == "champion4role" and len(data1) == 1:
                s2 = roles_by_champions[data1[0]].index(data2)
            return s1, s2

        priority_queue.sort(key=sort_key)

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
            selected_champion = random.choice(comp)
            comp_roles[role] = selected_champion
            off_role.append(selected_champion)
            comp.remove(selected_champion)

    stupidity_level = len(off_role)
    return comp_roles, stupidity_level, off_role


if __name__ == "__main__":
    print(best_fit_roles(
        ["Maokai", "Thresh", "Karthus", "Kalista", "Hecarim"]))
    print(best_fit_roles(["Singed", "Tristana", "Lux", "Zoe", "Poppy"]))
    print(best_fit_roles(["Pantheon", "Zac", "Lux", "Kaisa", "Urgot"]))
    print(best_fit_roles(["Pantheon", "Zac", "Lux", "KSante", "Urgot"]))
    print(best_fit_roles(
        ["Pantheon", "Zac", "Singed", "Tryndamere", "Karthus"]))
    print(best_fit_roles(["Singed", "Lux", "Lux", "Zoe", "Poppy"]))

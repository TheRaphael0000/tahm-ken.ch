import json
import numpy as np
from scipy.optimize import linear_sum_assignment

champions = json.load(
    open("static/cache_datadragon/champion.json", "rb"))["data"]


champions_ranked = json.load(
    open("static/cache_opgg/champions_ranked.json", "rb"))["data"]


# print(champions_ranked)
# print(champions)

champions_by_ig_name = {
    champion["name"]: champion
    for _, champion in champions.items()
}

champions_by_key = {
    int(champion["key"]): champion
    for _, champion in champions.items()
}

X_label = ["TOP", "JUNGLE", "MID", "ADC", "SUPPORT"]
Y_label = []
positions_champions_matrix = []

for champion_ranked in champions_ranked:
    champion = champions_by_key[champion_ranked["id"]]
    champion_id = champion["id"]

    Y_label.append(champion_id)

    pickrate = champion_ranked["average_stats"]["pick_rate"]
    champion_positions = set()

    position_playrate = {}

    sum_pickrate = 0
    for position in champion_ranked["positions"]:
        position_name = position["name"]
        position_pickrate = position["stats"]["pick_rate"]
        relative_position_pickrate = position_pickrate / pickrate
        relative_position_pickrate = 1 if relative_position_pickrate > 1 else relative_position_pickrate
        sum_pickrate += relative_position_pickrate
        champion_positions.add(position_name)
        position_playrate[position_name] = relative_position_pickrate

    remaining_pickrate = 1 - sum_pickrate
    remaining_positions = set(X_label) - champion_positions

    for position_name in remaining_positions:
        relative_position_pickrate = remaining_pickrate / \
            len(remaining_positions)
        position_playrate[position_name] = relative_position_pickrate

    positions_champions_matrix.append([position_playrate[y] for y in X_label])

positions_champions_matrix = np.array(positions_champions_matrix)


def best_fit_positions(comp):
    comp_position = {}
    attribution_score = 0
    off_role = []

    # input checks
    if len(set(comp)) != 5:
        raise Exception("Need 5 distinct champions")

    champ_indices = []
    for champion in comp:
        if champion not in Y_label:
            raise Exception(f"Invalid champion provided : {champion}")
        champ_indices.append(Y_label.index(champion))

    sub_matrix = positions_champions_matrix[champ_indices]

    row_indices, col_indices = linear_sum_assignment(-sub_matrix)

    for champion, r in zip(comp, col_indices):
        comp_position[X_label[r]] = champion

    for row, col in zip(row_indices, col_indices):
        champ_pickrate = sub_matrix[row, col]
        attribution_score += champ_pickrate
        if champ_pickrate < 0.1:
            off_role.append(Y_label[champ_indices[row]])

    return comp_position, attribution_score, off_role


if __name__ == "__main__":
    print(best_fit_positions(
        ["Maokai", "Thresh", "Karthus", "Kalista", "Hecarim"]))
    print(best_fit_positions(["Singed", "Tristana", "Lux", "Zoe", "Poppy"]))
    print(best_fit_positions(["Pantheon", "Zac", "Lux", "Kaisa", "Urgot"]))
    print(best_fit_positions(["Pantheon", "Zac", "Lux", "KSante", "Urgot"]))
    print(best_fit_positions(
        ["Blitzcrank", "Caitlyn", "Diana", "Gnar", "JarvanIV"]))
    print(best_fit_positions(
        ["Pantheon", "Zac", "Singed", "Tryndamere", "Karthus"]))
    print(best_fit_positions(["Singed", "Lux", "Lux", "Zoe", "Poppy"]))

from models.challenges_tools import complete_comp
from models.challenges_tools import find_challenges
from models.champions_positions import best_fit_positions

from collections import defaultdict
import json
import tqdm

comps = defaultdict(list)
previous_sizes = None

for comp in tqdm.tqdm(complete_comp(selected_champions=set([]), selected_challenges=set([]), limit=2e7)):
    comp_challenges = find_challenges(comp)
    if len(comp_challenges) < 6:
        continue

    comp_roles, attribution_score, off_role = best_fit_positions(comp)

    comp_str = str(sorted(list(comp)))
    key = f"{len(comp_challenges)} challenges compositions"
    comps[key].append((comp_roles, list(comp_challenges), attribution_score))

    current_sizes = [len(l) for l in comps.values()]
    if current_sizes != previous_sizes:
        print(current_sizes)

    previous_sizes = current_sizes


comps = dict(comps)

for k, v in comps.items():
    print(k, len(v))

json.dump(comps, open("static/cache_compositions/compositions.json", "w"))

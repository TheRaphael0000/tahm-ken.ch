# challenges intersection league

trying to create a gui which help to optimize the new teamwork challenges in league of legends by finding compositions that contain the most challenges.

still wip, you can pr if you want.

or use it on https://tahm-ken.ch/

## todo
- [ ] show challenges for each champions when hovering them
- [ ] block api route when too many request from same client (look into the flask_limiter package)
- [ ] responsiveness for mobile
- [ ] update table sorting and add visual clue of the current sort
- [ ] add a caching system for the API calls, see if its better to use cassiopeia instead of riotwatcher
- [ ] use genetic algorithms to find the best compositions to try to avoid having always the same champs in the best compositions
- [ ] User eXperience (help needed)
- [ ] multi-language


## done
- [x] collect the data
- [x] parse the data
- [x] create a basic ui
- [x] add functions to intersect the sets
- [x] update the ui according to the challenge selections
- [x] copy the selected champion into the clipboard
- [x] update the ui according to the champion selections
- [x] add a page to good composition found for each challenges that require 5 specifics champions
- [x] add a filter for specifics champions in optimized compositions
- [x] show challenges for each champions when selecting them 
- [x] find a way to implement Variety's Overrated
- [x] fetch from Riot API current challenges
- [x] in the compositions, update the filter to only show available champs
- [x] search for champions when typing letters
- [x] add tooltips for the challenges, idea from PureImplosion on Reddit
- [x] filter out champions in compositions, idea from DOOGLAK on Reddit
- [x] recompute the optimized composition for "Variety's Overrated", idea from Konstamonsta on Reddit
- [x] replace the space in the name of the compositions by underscores or dashes
- [x] use cdragon icon for the challenge


## install
you need python

```
make install
```

you also need `compositions.json` which can be obtained by running `brute_force_compositions.ipynb` with jupyter

or

you can download the current version on https://tahm-ken.ch/static/compositions.json

## run
```
python app.py
```

## thanks

people who directly helped the project (more than feedbacks):

- thanks to @celiendonze and @Etiouse for helping me populate the initial `challenges.json`
- thanks to @Pomarine for reviewing and correcting the `challenges.json` file
- thanks to @Naralas for fixing paths in `brute_force_compositions.ipynb`

people who gave feedback that were implemented/bug fixed:

- 
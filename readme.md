# challenges intersection league

trying to create an app which help to optimize the teamwork challenges in league of legends by finding compositions that contain the most challenges.

still wip, you can pr if you want.

## todo
- [ ] (bugfix) show points for harmony and globetrotter
- [ ] responsiveness for mobile
- [ ] update table sorting and add visual clue of the current sort
- [ ] add a caching system for the API calls, see if its better to use cassiopeia instead of riotwatcher
- [ ] create a batch file for windows install
- [ ] User eXperience (help needed)
- [ ] multi-language


## done
- [x] show challenges for each champions when ~~hovering~~ selecting them (act like you added them)
- [x] have a multisearch feature like op.gg
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
- [x] add a Q&A
- [x] add summoners icon and challenge progression when searching for summoner
- [x] block api route when too many request from same client (look into the flask_limiter package)
- [x] custom compositions (algo that find good comps depending on the masteries)
- [x] use role identifications for ordering the champions in the optimized compositions
- [x] move the "how to use" on the corresponding pages (modal dialog)
- [x] add more filters for optimized compositions (for champions role for example) -> became the stupidity level metric
- [x] select the 'correct' server by default depending on the ip address

## install
you need python 3

```
make install
```

the makefile will download the current `compositions.json` which can be obtained by running `compositions.ipynb` with jupyter.

create `config.json` from `config_sample.json` and fill it in.

keys:
- app_secret_key : `python -c "import secrets; print(secrets.token_hex(24))"`
- riot_api_key : mandatory, for the League profiles inspections, https://developer.riotgames.com/
- ipinfo_token : not mandatory, to select the default server, https://ipinfo.io/
- discord_bot_token : not mandatory, for the discord communities, https://discord.com/developers/applications

i'll try to make the riot api key not mandatory...

## run
```
python app.py
```

## thanks

people who directly helped the project (more than feedbacks):

- thanks to @celiendonze and @Etiouse for helping me populate the initial `challenges.json`
- thanks to @Pomarine for reviewing and correcting the `challenges.json` file
- thanks to @Naralas for fixing paths in `brute_force_compositions.ipynb`
- thanks to @DarkIntaqt for fixing a few typos and adding better meta tags

people who gave feedback that were implemented/bug fixed:

- u/PureImplosion
- u/DOOGLAK
- u/Konstamonsta
- Scraf#2052
- Amy#5664
- NotDay#2927
- (NA) Carbunkle#0740
- DarkIntaqt#2858

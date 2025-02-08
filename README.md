# Tahm-Ken.ch

The goal of this WebApp is to facilitate the completion of the _Harmony_ and _Globetrotter_ teamwork challenges in League of Legends.

If you want to help, don't hesitate! The projected is quite a mess right now though, so good luck!

# Dev setup

I've tested this install setup on Windows Ubuntu WSL, but this probably also works on Linux or Mac.
For Windows install WSL or good luck!

```bash
git clone git@github.com:TheRaphael0000/tahm-ken.ch.git # or your fork URL
cd tahm-ken.ch
```

## Install dependencies

```bash
# python if you don't have it
apt install python3 python3-pip python3-venv -y

# create a venv and install dependencies
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Caches

Some data are not directly included in this repository and you need to fetch them yourself:

### Mandatory caches

```bash
# download latest playrates from opgg
python3 cache_opgg.py

# download latest datadragon files (can take a few minutes)
python3 cache_datadragon.py

# download the latest precomputed caches file so you don't have to compute them yourself
mkdir static/cache/compositions
curl https://tahm-ken.ch/static/cache/compositions/compositions.json > static/cache/compositions/compositions.json
# or you can compute it yourself by running:
# python3 cache_compositions.py

# download the latest challenge config file used on the server
mkdir static/cache/riot_api
curl https://tahm-ken.ch/static/cache/riot_api/challenges_config.json > static/cache/riot_api/challenges_config.json
# if you set the Riot API key run this instead:
# python3 cache_riot_api.py
```

### Optional caches

#### LCU data
This is a bit of a weird step. You must run this from Windows. Since you are probably using WSL, you have to map WSL as a windows drive and then run it from there.
If you really want to do this and you dont understand what I just said, contact me on discord (theraphael0000).
You must have your League of Legends client updated and running, more info here: https://riot-api-libraries.readthedocs.io/en/latest/lcu.html
```
# optional: download latest challenge game only data
python cache_lcu.py
```

#### Geo IP

If you want to automatically select the default server depending on the IP of the client.
Download `GeoLite2-Country.mmdb` and put it in `static/cache/geo`.
Let you google how to get it.

## Optional API keys

```bash
# create a config file from the sample
cp .env_sample .env
```

These require manual steps on the given website.

-   `riot_api_key` : for the League profiles inspections, https://developer.riotgames.com/

## Run the dev env

```bash
source venv/bin/activate
python3 app.py
```

## CD

A CD script that update the website on a server through ssh. I guess nobody can access the server except me, so probably not useful for you :)

```
python3 fabfile.py # need ssh-key for tahm-ken.ch :)
```

# Thanks

People who directly helped the project (more than feedbacks):

-   thanks to @celiendonze and @Etiouse for helping me populate the initial `challenges.json`
-   thanks to @Pomarine for reviewing and correcting the `challenges.json` file
-   thanks to @Naralas for fixing paths in `brute_force_compositions.ipynb`
-   thanks to @DarkIntaqt for fixing a few typos and adding better meta tags
-   thanks to @DarkIntaqt for adding the share composition feature
-   thanks to @AndiZandi for improving UX in the multi-search

People who gave feedback that were implemented/bug fixed:

-   u/PureImplosion
-   u/DOOGLAK
-   u/Konstamonsta
-   Scraf#2052
-   Amy#5664
-   NotDay#2927
-   (NA) Carbunkle#0740
-   DarkIntaqt#2858

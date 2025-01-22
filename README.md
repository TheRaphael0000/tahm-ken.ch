# Tahm-Ken.ch

The goal of this WebApp is to facilitate the completion of the _Harmony_ and _Globetrotter_ teamwork challenges in League of Legends.

If you want to help, don't hesitate! The projected is quite a mess right now though, so good luck!

## Dev setup

I've tested this install setup on Windows Ubuntu WSL, but this probably also works on Linux or Mac.
For Windows install WSL or good luck!

```bash
git clone git@github.com:TheRaphael0000/tahm-ken.ch.git # or your fork URL
cd tahm-ken.ch
```

### Install dependencies

```bash
# python if you don't have it
apt install python3 python3-pip

# create a venv and install dependencies
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

### Configs

```bash
# create a config file from the sample
cp config_sample.json config.json

# create a the flask secret and set it in the config file
sed -i 's/"app_secret_key": ""/"app_secret_key": "'$(python3 -c "import secrets; print(secrets.token_hex(24))")'"'/g config.json
```

**Optional API keys**. These require manual steps on the given website. You can skip those for most cases!

-   `riot_api_key` : for the League profiles inspections, https://developer.riotgames.com/
-   `discord_bot_token` : for the discord communities, https://discord.com/developers/applications

### Update caches

```bash
# download latest playrates from opgg
python3 cache_opgg.py

# download latest datadragon files (can take a few minutes)
python3 cache_datadragon.py

# download latest challenge game only data (you must have your League of Legends client, more info here: https://riot-api-libraries.readthedocs.io/en/latest/lcu.html)
python3 cache_lcu.py

# download the latest precomputed caches file so you don't have to compute them yourself
mkdir static/cache_compositions
curl https://tahm-ken.ch/static/cache_compositions/compositions.json > static/cache_compositions/compositions.json
# or you can compute it yourself by running:
# python3 cache_compositions.py

# download the latest challenge config file used on the server
mkdir static/cache_riot_api
curl https://tahm-ken.ch/static/cache_riot_api/challenges_config.json > static/cache_riot_api/challenges_config.json
# if you set the Riot API key run this instead:
# python3 cache_riot_api.py
```

### GeoIP

If you want to automatically select the default server depending on the IP of the client.
Download `GeoLite2-Country.mmdb` and put it in the root folder.
Let you google how to get it.

### Run the dev env

```bash
source venv/bin/activate
python3 app.py
```

## CD

A CD script that update the website on a server through ssh. I guess nobody can access the server except me, so probably not useful for you :)

```
python3 fabfile.py # need ssh-key for tahm-ken.ch :)
```

## Thanks

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

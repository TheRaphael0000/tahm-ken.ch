#!/usr/bin/env python

import click
import fabric
from pathlib import Path
import os

python_bin = "venv/bin/python"
pip_bin = "venv/bin/pip"
repo_folder = "/var/www/tahm-ken.ch/www.tahm-ken.ch"
c = fabric.Connection(host="tahm-ken.ch", user="root", port=22)

with c.cd(repo_folder):
    if click.confirm("Update code?", default=True):
        before_pulling = c.run("git rev-parse HEAD", hide=True).stdout
        before_pulling = before_pulling.replace('\n', '')

        git_status = c.run("git status --short")
        if len(git_status.stdout) > 0:
            if click.confirm("Stash and deploy to main ?", default=True):
                c.run("git stash")
            else:
                print("Deployment aborted.")
                exit()

        # update main
        print(f"Updating code...")
        c.run("git checkout main")
        c.run("git pull")

        # upgrade modules if needed
        command = f"git diff {before_pulling} requirements.txt"
        diff_on_requirements = c.run(command, hide=True)
        if len(diff_on_requirements.stdout) > 0:
            print(f"Upgrading pip requirements...")
            c.run(f"{pip_bin} install -r requirements.txt --upgrade")
    print()

    if click.confirm("Update cache?", default=True):
        print("Updating Riot API cache...")
        c.run(f"{python_bin} cache_riot_api.py")
        print()

        print("Updating Datadragon cache...")
        c.run(f"{python_bin} cache_datadragon.py")
        print()

        print("Updating Opgg cache...")
        c.run(f"{python_bin} cache_opgg.py")
        print()

    file = "static/cache/compositions/compositions.json"
    if click.confirm(f"Update {file}?", default=True):
        print(f"Copying {file}...")
        # couldn't make it work with the c.cd()
        c.put(file, repo_folder + "/" + file)
        print()

    if click.confirm(f"Restart gunicorn service?", default=True):
        print(f"Restarting gunicorn service...")
        c.run("systemctl restart www.tahm-ken.ch_gunicorn.service")

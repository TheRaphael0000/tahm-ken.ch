#!/usr/bin/env python

import click
import fabric

repo_folder = "/var/www/tahm-ken.ch/www.tahm-ken.ch"


def deploy(c):
    with c.cd(repo_folder):
        current_commit = c.run("git rev-parse HEAD",
                               hide=True).stdout.replace('\n', '')

        git_status = c.run("git status --short")

        if len(git_status.stdout) > 0:
            stash = click.confirm("Stash and deploy to main ?", default=True)
            if stash:
                c.run("git stash")
            else:
                print("Deployment aborted.")
                exit()

        # update main
        c.run("git checkout main")
        c.run("git pull")

        # upgrade modules if needed
        diff_on_requirements = c.run(
            f"git diff {current_commit} requirements.txt", hide=True)
        if len(diff_on_requirements.stdout) > 0:
            c.run("pip install -r requirements.txt --upgrade")

    with c.cd(repo_folder):
        c.run("python cache_riot_api.py")
        c.run("python cache_datadragon.py")
        c.run("python cache_opgg.py")

    c.run("systemctl restart www.tahm-ken.ch_gunicorn.service")


c = fabric.Connection(host="tahm-ken.ch", user="root", port=22)
deploy(c)

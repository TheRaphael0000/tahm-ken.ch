#!/usr/bin/env python

import click
import fabric


def deploy(c):
    with c.cd("/var/www/tahm-ken.ch/www.tahm-ken.ch"):
        c.run("git status")
        if not click.confirm("Stash and deploy to main ?", default=True):
            exit()
        c.run("git stash")
        c.run("git checkout main")
        c.run("git pull")
        if click.confirm("Upgrade modules ?", default=False):
            c.run("pip install -r requirements.txt --upgrade")
        c.run("systemctl restart www.tahm-ken.ch_gunicorn.service")


c = fabric.Connection(host="tahm-ken.ch", user="root", port=22)
deploy(c)

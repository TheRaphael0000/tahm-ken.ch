# challenges intersection league

trying to create a gui to find intersection in the league of legends new teamwork challenges.

still wip, you can pr if you want.

## todo
- [x] collect the data
- [x] parse the data
- [x] create a basic ui
- [x] add functions to intersect the sets
- [ ] update the ui according to the selections


## install
you need python

you can download champion images at https://developer.riotgames.com/docs/lol#data-dragon
put the champion square image in static/champion

```
python -m pip install -r requirements.txt
```

## run
```
export FLASK_ENV=development
export FLASK_APP=webui
flask run
```

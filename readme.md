# challenges intersection league

trying to create a gui which help to optimize the new teamwork challenges in league of legends by finding compositions that contain the most challenges.

still wip, you can pr if you want.

or use it on https://challsection.theraphael0000.ch/

## todo
- [x] collect the data
- [x] parse the data
- [x] create a basic ui
- [x] add functions to intersect the sets
- [x] update the ui according to the challenge selections
- [x] copy the selected champion into the clipboard
- [x] update the ui according to the champion selections
- [x] add a page to good composition found for each challenges that require 5 specifics champions
- [x] add a filter for specifics champions in optimized compositions
- [ ] show challenges for each champions when hovering them 
- [ ] find a way to implement Variety's Overrated
- [ ] use genetic algorithms to find the best compositions to try to avoid having always the same champs in the best compositions


## install
you need python

```
make install
```

you also need `compositions.json` which can be obtained by running `brute_force_compositions.ipynb` with jupyter

or

you can download the current version on https://challsection.theraphael0000.ch/static/compositions.json

## run
```
python app.py
```

## thanks

- thanks to @celiendonze and @Etiouse for helping me populate the initial `challenges.json`
- thanks to @Pomarine for reviewing and correcting the `challenges.json` file

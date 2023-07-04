install:
	python -m pip install -r requirements.txt
	python data/datadragon.py
	python api_cache.py
	cd static && wget https://tahm-ken.ch/static/compositions.json
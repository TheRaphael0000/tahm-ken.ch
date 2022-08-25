install:
	python -m pip install -r requirements.txt
	python datadragon.py
	cd static && wget https://tahm-ken.ch/static/compositions.json
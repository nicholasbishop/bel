run:
	venv/bin/python demo.py

lint:
	venv/bin/pylint -rn bel demo.py -d missing-docstring -d protected-access -d no-member -d invalid-name

virtualenv:
	virtualenv-3.4 venv
	. venv/bin/activate && pip3 install -r requirements.txt

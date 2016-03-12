run:
	venv/bin/python demo.py

lint:
	venv/bin/pylint -rn bel demo.py -d locally-disabled,missing-docstring,too-few-public-methods

virtualenv:
	virtualenv-3.4 venv
	. venv/bin/activate && pip3 install -r requirements.txt

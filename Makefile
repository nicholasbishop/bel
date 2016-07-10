run: venv
	venv/bin/python -m demo

lint: venv
	venv/bin/python -m pylint bel demo	

venv:
	virtualenv-3.5 venv
	pip install --requirements requirements.txt
	pip install --requirements requirements_dev.txt

.PHONY: lint run

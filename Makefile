run: venv
	venv/bin/python -m demo

venv:
	virtualenv-3.5 venv
	pip install --requirements requirements.txt

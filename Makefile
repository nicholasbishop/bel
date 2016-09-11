run: venv
	venv/bin/python -m demo

# TODO(nicholasbishop): remove these disables when it makes sense to
lint: venv
	venv/bin/python -m pylint -d fixme,missing-docstring bel demo

test: venv
	venv/bin/python -m unittest discover --verbose

venv:
	virtualenv-3.5 venv
	venv/bin/pip install -r requirements.txt
	venv/bin/pip install -r requirements_dev.txt

.PHONY: lint run test

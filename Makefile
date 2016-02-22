all:

run:
	venv/bin/python me2.py

lint:
	pylint -rn pybliz -d missing-docstring -d protected-access -d no-member -d invalid-name

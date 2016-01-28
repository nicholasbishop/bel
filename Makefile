all:

lint:
	pylint -rn pybliz -d missing-docstring -d protected-access -d no-member -d invalid-name

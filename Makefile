.PHONY: build

PIP = pip
PYTHON = python

build:
	${PYTHON} -m build

install:
	${PIP} install . -U

install-editable:
	${PIP} install -e . --config-settings editable_mode=compat

test:
	ruff check .
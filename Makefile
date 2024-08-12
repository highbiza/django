.PHONY: fail-if-no-virtualenv all install dev lint test black

all: install migrate collectstatic

fail-if-no-virtualenv:
ifndef VIRTUAL_ENV # check for a virtualenv in development environment
ifndef PYENVPIPELINE_VIRTUALENV # check for jenkins pipeline virtualenv
$(error this makefile needs a virtualenv)
endif
endif

ifndef PIP_INDEX_URL
PIP_INDEX_URL=https://pypi.uwkm.nl/oxyan/oscar/+simple/
endif


install: fail-if-no-virtualenv
	pip install -e .
	pip install -r tests/requirements/py3.txt

test: fail-if-no-virtualenv
	@coverage run --source='django' tests/runtests.py
	@coverage report
	@coverage xml
	@coverage html

clean: ## Remove files not in source control
	find . -type f -name "*.pyc" -delete
	rm -rf nosetests.xml coverage.xml htmlcov *.egg-info *.pdf dist violations.txt

package: clean
	rm -rf dist/
	rm -rf build/
	pip wheel .

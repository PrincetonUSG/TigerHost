develop: install-requirements install-test-requirements

install-requirements:
	pip install "click>=6.0" # for some reason, causes dependency issues
	pip install -e .

install-test-requirements: install-requirements
	pip install "file://`pwd`#egg=deploy[tests]"

deploy-pypi:
	python setup.py register -r pypi && python setup.py sdist upload -r pypi

deploy-pypi-test:
	python setup.py register -r pypitest && python setup.py sdist upload -r pypitest

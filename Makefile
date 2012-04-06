.PHONY: install
install:
	python setup.py install

.PHONY: build
build:
	python setup.py build

.PHONY: sdist
sdist:
	python setup.py sdist

.PHONY: upload
upload:
	python setup.py sdist upload

.PHONY: clean
clean:
	rm -rf dist build *.egg-info python-piwik-tracking-*

.PHONY: test
test:
	python piwiktracking/tests.py

.PHONY: html
html:
	make -C doc html

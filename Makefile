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
	rm -rf dist build *.egg-info python-piwikapi-*
	find . -name *.pyc -print0 | xargs -0 rm -f
	make -C doc clean

.PHONY: test
test:
	python piwikapi/tests/

.PHONY: html
html:
	make -C doc html

version := $(shell python -c "exec(open('pykeepass/version.py').read());print(__version__)")

.PHONY: dist
dist:
	python setup.py sdist bdist_wheel

.PHONY: pypi
pypi: dist
	twine upload dist/pykeepass-$(version).tar.gz

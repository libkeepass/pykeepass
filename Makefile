version := $(shell python -c "exec(open('pykeepass/version.py').read());print(__version__)")

.PHONY: dist
dist:
	python setup.py sdist bdist_wheel

.PHONY: pypi
pypi: dist
	twine upload dist/pykeepass-$(version).tar.gz

.PHONY: docs
docs:
	lazydocs pykeepass --overview-file README.md
	ghp-import -f -p -b docs docs

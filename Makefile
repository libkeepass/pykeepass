.ONESHELL:
.SHELLFLAGS = -ec
.SILENT:
version := $(shell python -c "import tomllib;print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")

.PHONY: dist
dist:
	python -m build

.PHONY: release
release: lock dist
	# check that changelog is updated
	if ! grep ${version} CHANGELOG.rst
	then
		echo "Changelog doesn't seem to be updated! Quitting..."
		exit 1
	fi
	twine upload -u __token__ dist/pykeepass-$(version)*
	gh release create pykeepass-$(version) dist/pykeepass-$(version)*

.PHONY: lock
lock:
	# make a requirements.txt lockfile
	rm -rf .venv_lock
	virtualenv .venv_lock
	. .venv_lock/bin/activate
	pip install .[test]
	python tests/tests.py
	pip freeze > requirements.txt


.PHONY: docs
docs:
	lazydocs pykeepass --overview-file README.md
	ghp-import -f -p -b docs docs

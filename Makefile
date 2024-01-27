.ONESHELL:
.SILENT:
version := $(shell python -c "import tomllib;print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")

.PHONY: dist
dist:
	python -m build

.PHONY: release
release: dist
	# check that changelog is updated
	if ! grep ${version} CHANGELOG.rst
	then
		echo "Changelog doesn't seem to be updated! Quitting..."
		exit 1
	fi
	twine upload dist/pykeepass-$(version)*
	gh release create pykeepass-$(version) dist/pykeepass-$(version)*

.PHONY: docs
docs:
	lazydocs pykeepass --overview-file README.md
	ghp-import -f -p -b docs docs

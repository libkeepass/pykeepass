.PHONY: dist
dist:
	poetry build

.PHONY: pypi
pypi: dist
	twine upload --skip-existing dist/pykeepass-*

.PHONY: docs
docs:
	lazydocs pykeepass --overview-file README.md
	ghp-import -f -p -b docs docs

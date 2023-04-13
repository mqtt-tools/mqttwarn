# ============
# Main targets
# ============


# -------------
# Configuration
# -------------

$(eval venvpath     := .venv)
$(eval pip          := $(venvpath)/bin/pip)
$(eval python       := $(venvpath)/bin/python)
$(eval pytest       := $(venvpath)/bin/pytest)
$(eval twine        := $(venvpath)/bin/twine)
$(eval sphinx       := $(venvpath)/bin/sphinx-build)
$(eval sphinx-autobuild := $(venvpath)/bin/sphinx-autobuild)
$(eval isort        := $(venvpath)/bin/isort)
$(eval black        := $(venvpath)/bin/black)
$(eval poe          := $(venvpath)/bin/poe)

# Setup Python virtualenv
setup-virtualenv:
	@test -e $(python) || python3 -m venv $(venvpath)
	$(pip) install versioningit


# -------
# Testing
# -------

# Run the main test suite
test: install-tests
	@$(poe) test

test-refresh: install-tests test

test-junit: install-tests
	@$(pytest) -vvv tests --junit-xml .pytest_results/pytest.xml

test-coverage: install-tests
	@$(pytest) --cov-report html:.pytest_results/htmlcov


# ----------------------
# Linting and Formatting
# ----------------------
format: install-releasetools
	$(poe) format


# -------
# Release
# -------

# Release this piece of software
release: push build pypi-upload


# -------------
# Documentation
# -------------

# Build the documentation
docs-html: install-doctools
	cd docs; make html

docs-serve:
	cd docs/_build/html; python3 -m http.server

docs-autobuild: install-doctools
	$(sphinx-autobuild) --open-browser docs docs/_build


# ===============
# Utility targets
# ===============
push:
	git push && git push --tags

build: install-releasetools
	@$(python) -m build

pypi-upload: install-releasetools
	$(twine) upload --skip-existing --verbose dist/*{.tar.gz,.whl}

install-doctools:
	@test -e $(python) || python3 -m venv $(venvpath)
	$(pip) install --quiet --upgrade --requirement=docs/requirements.txt

install-releasetools: setup-virtualenv
	@$(pip) install --requirement requirements-release.txt --upgrade

install-tests: setup-virtualenv
	@test -e $(pytest) || $(pip) install --editable=.[test,develop] --upgrade
	@touch $(venvpath)/bin/activate
	@mkdir -p .pytest_results

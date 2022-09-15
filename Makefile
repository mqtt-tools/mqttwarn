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
$(eval bumpversion  := $(venvpath)/bin/bumpversion)
$(eval twine        := $(venvpath)/bin/twine)
$(eval sphinx       := $(venvpath)/bin/sphinx-build)
$(eval isort        := $(venvpath)/bin/isort)
$(eval black        := $(venvpath)/bin/black)
$(eval poe          := $(venvpath)/bin/poe)

# Setup Python virtualenv
setup-virtualenv:
	@test -e $(python) || python3 -m venv $(venvpath)


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
# Synopsis:
#   make release bump=minor  (major,minor,patch)
release: bumpversion push build pypi-upload


# -------------
# Documentation
# -------------

# Build the documentation
docs-html: install-doctools
	touch doc/index.rst
	export SPHINXBUILD="`pwd`/$(sphinx)"; cd doc; make html


# ===============
# Utility targets
# ===============
bumpversion: install-releasetools
	@$(bumpversion) $(bump)

push:
	git push && git push --tags

build: install-releasetools
	@$(python) -m build

pypi-upload: install-releasetools
	$(twine) upload --skip-existing --verbose dist/*{.tar.gz,.whl}

install-doctools: setup-virtualenv
	@$(pip) install --requirement requirements-docs.txt --upgrade

install-releasetools: setup-virtualenv
	@$(pip) install --requirement requirements-release.txt --upgrade

install-tests: setup-virtualenv
	@test -e $(pytest) || $(pip) install --editable=.[test,develop] --upgrade
	@touch $(venvpath)/bin/activate
	@mkdir -p .pytest_results

import importlib
import sys

import pytest

# Import custom fixtures.
from mqttwarn.testing.fixtures import mqttwarn_service as srv  # noqa:F401


@pytest.fixture
def fake_filesystem(fs):  # pylint:disable=invalid-name
    try:
        fs.create_dir("/tmp")
    except Exception:
        pass
    yield fs


@pytest.fixture
def without_jinja():

    # Emulate removal of `jinja2` package.
    # https://stackoverflow.com/a/65163627
    backup = sys.modules["jinja2"]
    sys.modules["jinja2"] = None
    importlib.reload(sys.modules["mqttwarn.core"])

    yield

    # Restore `jinja2` package.
    sys.modules["jinja2"] = backup
    importlib.reload(sys.modules["mqttwarn.core"])

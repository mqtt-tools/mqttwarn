import importlib
import shutil
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


@pytest.fixture
def mqttwarn_bin():
    """
    Find `mqttwarn` executable, located within the inline virtualenv.
    """

    path_candidates = [None, ".venv/bin", r".venv\Scripts"]
    for path_candidate in path_candidates:
        mqttwarn_bin = shutil.which("mqttwarn", path=path_candidate)
        if mqttwarn_bin is not None:
            return mqttwarn_bin

    raise FileNotFoundError(f"Unable to discover 'mqttwarn' executable within {path_candidates}")

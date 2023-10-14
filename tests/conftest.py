# -*- coding: utf-8 -*-
# (c) 2018-2023 The mqttwarn developers
import importlib
import os
import pathlib
import shutil
import sys
import typing as t
from tempfile import NamedTemporaryFile

import pytest

# Needed to make Apprise not be mocked too much.
from mqttwarn.services.apprise_util import get_all_template_argument_names  # noqa:F401

# Import custom fixtures.
from mqttwarn.testing.fixtures import mqttwarn_service as srv  # noqa:F401
from tests.fixtures.ntfy import ntfy_service  # noqa:F401


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
def without_ssl():

    # Emulate removal of `ssl` package.
    # https://stackoverflow.com/a/65163627
    backup = sys.modules["ssl"]
    sys.modules["ssl"] = None
    importlib.reload(sys.modules["mqttwarn.configuration"])

    yield

    # Restore `jinja2` package.
    sys.modules["ssl"] = backup
    importlib.reload(sys.modules["mqttwarn.configuration"])


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


@pytest.fixture()
def tmp_ini(tmp_path) -> pathlib.Path:
    """
    Provide temporary INI files to test cases.
    """
    filepath = tmp_path.joinpath("testdrive.ini")
    return filepath


@pytest.fixture
def attachment_dummy() -> t.Generator[t.IO[bytes], None, None]:
    """
    Provide a temporary file to the test cases to be used as an attachment with defined content.
    """
    tmp = NamedTemporaryFile(suffix=".txt", delete=False)
    tmp.write(b"foo")
    tmp.close()
    yield tmp
    os.unlink(tmp.name)

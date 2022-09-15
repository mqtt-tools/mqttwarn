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

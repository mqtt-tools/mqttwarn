import pytest

# Import fixtures
from mqttwarn.testing.fixtures import mqttwarn_service as srv  # noqa


@pytest.fixture
def fake_filesystem(fs):  # pylint:disable=invalid-name
    try:
        fs.create_dir("/tmp")
    except:
        pass
    yield fs

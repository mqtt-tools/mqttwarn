import pytest

from tests.util import FakeResponse


@pytest.fixture
def mock_urlopen_success(mocker):
    return mocker.patch("urllib.request.urlopen", return_value=FakeResponse(data=b'{"status": 1}'))


@pytest.fixture
def mock_urlopen_failure(mocker):
    return mocker.patch("urllib.request.urlopen", return_value=FakeResponse(data=b'{"status": 6}'))

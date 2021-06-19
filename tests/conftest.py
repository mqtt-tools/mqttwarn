import logging

import pytest

from mqttwarn.core import Service


@pytest.fixture
def srv():
    """
    A service instance for propagating to the plugin.
    """
    logger = logging.getLogger(__name__)
    return Service(mqttc=None, logger=logger)

import logging

import pytest

from mqttwarn.model import Service


@pytest.fixture
def mqttwarn_service():
    """
    A service instance for propagating to the plugin.
    """
    logger = logging.getLogger(__name__)
    # FIXME: Should propagate `mqttwarn.core.globals()` to `mwcore`.
    return Service(mqttc=None, logger=logger, mwcore={}, program="mqttwarn-testdrive")

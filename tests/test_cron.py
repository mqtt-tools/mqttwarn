from unittest.mock import Mock, call

from mqttwarn.cron import PeriodicThread
from tests.util import delay


def test_periodic_thread_success_now():
    """
    Proof that the `cron.PeriodicThread` implementation works as intended.
    """
    callback = Mock()
    pt = PeriodicThread(callback=callback, period=0.05, name="foo", srv="SRVDUMMY", now=True, options={"foo": "bar"})
    pt.start()
    delay(0.35)
    pt.cancel()
    pt.join()

    # Timer should have been called at least two times.
    assert [
        call("SRVDUMMY", options={"foo": "bar"}),
        call("SRVDUMMY", options={"foo": "bar"}),
    ] in callback.mock_calls


def test_periodic_thread_success_not_now():
    """
    Proof that the `cron.PeriodicThread` implementation works as intended.
    """
    callback = Mock()
    pt = PeriodicThread(callback=callback, period=0.05, name="foo", srv="SRVDUMMY", now=False, options={"foo": "bar"})
    pt.start()
    delay(0.35)
    pt.cancel()
    pt.join()

    # Timer should have been called at least two times.
    assert [
        call("SRVDUMMY", options={"foo": "bar"}),
        call("SRVDUMMY", options={"foo": "bar"}),
    ] in callback.mock_calls


def test_periodic_thread_failure(caplog):
    """
    Proof that the `cron.PeriodicThread` implementation croaks as intended.
    """

    def callback(srv, *args, **kwargs):
        assert srv == "SRVDUMMY"
        assert args == ()
        assert kwargs == {"options": {"foo": "bar"}}
        raise ValueError("Something failed")

    pt = PeriodicThread(callback=callback, period=0.005, name="foo", srv="SRVDUMMY", now=True, options={"foo": "bar"})
    pt.start()
    delay(0.0125)
    pt.cancel()
    pt.join()

    assert "Exception while running periodic thread 'foo'" in caplog.messages
    assert "ValueError: Something failed" in caplog.text

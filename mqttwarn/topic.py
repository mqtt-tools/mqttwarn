# (c) 2014-2023 The mqttwarn developers

import logging
import threading
import time
import typing as t

logger = logging.getLogger(__name__)


class TopicTimeout(threading.Thread):
    """
    A thread handling timeouts on mqtt topics
    """

    def __init__(
        self,
        topic: t.Optional[str] = None,
        timeout: t.Optional[int] = 1,
        section: t.Optional[str] = None,
        notify_only_on_timeout: t.Optional[bool] = False,
        on_timeout: t.Optional[t.Callable] = None
    ):
        threading.Thread.__init__(self)
        self.topic = topic
        self.timeout = timeout
        self.section = section
        self.notify_only_on_timeout = notify_only_on_timeout
        self.last_state_timeout = False
        self._on_timeout = on_timeout
        self._restart_event = threading.Event();
        self._stop_event = threading.Event()

    def run(self):
        logger.debug("Starting thread %s for topic %s" % (self.name, self.topic))
        # The outer loop runs until the thread receives a stop signal
        # See: https://stackoverflow.com/questions/323972/is-there-any-way-to-kill-a-thread
        # The outer loop is used to reset the timeout after a message was received
        while not self._stop_event.is_set():
            timeout = self.timeout
            # The inner loop runs until a stop signal is received or a message is received
            # It uses the same logic as the outer loop for the signal handling
            while True:
                if self._stop_event.is_set():
                    # End the inner loop on stop signal
                    break
                if self._restart_event.is_set():
                    # When a thread receives the reset signal, a message was received before the timeout.
                    # End the inner loop on reset signal, but before check what to do with the message.
                    # If the topic notifies only about timeout / no timeout and the last state was timeout
                    # a notification for the OK state should be published, otherwise just restart the thread
                    # and the received message will be handled by mqttwarn.
                    if self.last_state_timeout and self.notify_only_on_timeout:
                        logger.debug("%s received message for topic %s before timeout" % (self.name, self.topic))
                        message = "Message received for topic %s within %i" % (self.topic, self.timeout)
                        self.last_state_timeout = False
                        self._on_timeout(self.section, self.topic, message.encode('UTF-8'))
                    self._restart_event = threading.Event()
                    break
                logger.debug("%s waiting... %i" % (self.name, timeout))
                time.sleep(1)
                timeout = timeout - 1
                if timeout == 0:
                    logger.debug("%s timeout for topic %s" % (self.name, self.topic))
                    message = "Timeout for topic %s after %i" % (self.topic, self.timeout)
                    self.last_state_timeout = True
                    self._on_timeout(self.section, self.topic, message.encode('UTF-8'))
                    break

    def restart(self):
        logger.debug("Restarting timeout thread for %s (timeout %i)" % (self.topic, self.timeout))
        self._restart_event.set()

    def stop(self):
        logger.debug("Stopping timeout thread for %s" % (self.topic))
        self._stop_event.set()

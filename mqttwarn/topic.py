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
        on_timeout: t.Optional[t.Callable] = None
    ):
        threading.Thread.__init__(self)
        self.topic = topic
        self.timeout = timeout
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
                    break
                if self._restart_event.is_set():
                    self._restart_event = threading.Event();
                    break
                logger.debug("%s waiting... %i" % (self.name, timeout))
                time.sleep(1)
                timeout = timeout - 1;
                if timeout == 0:
                    logger.debug("%s timeout for topic %s" % (self.name, self.topic))
                    message = "Timeout for topic %s after %i" % (self.topic, self.timeout)
                    self._on_timeout(self.topic, message.encode('UTF-8'))
                    break

    def restart(self):
        logger.debug("Restarting timeout thread for %s (timeout %i)" % (self.topic, self.timeout))
        self._restart_event.set()

    def stop(self):
        logger.debug("Stopping timeout thread for %s" % (self.topic))
        self._stop_event.set()

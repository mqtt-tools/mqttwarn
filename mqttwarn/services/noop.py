from mqttwarn.model import Service, ProcessorItem


def plugin(srv: Service, item: ProcessorItem) -> bool:
    """
    An mqttwarn plugin with little overhead, suitable for unit- and integration-testing.
    """
    if hasattr(item, "message") and item.message and "fail" in item.message:
        srv.logging.error("Failed sending message using noop")
        return False
    else:
        srv.logging.info("Successfully sent message using noop")
        return True

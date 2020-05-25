import json


def togglestate(topic, payload, section, srv):
    filename = "warntoggle.json"
    default_topicblock = False

    try:
        with open(filename) as infile:
            toggles = json.load(infile)
            infile.close()

        if topic in toggles:
            # file found, topic found
            topicblock = toggles[topic]
            srv.logging.debug('togglestate() was called from the {} section and found {} in {}'.format(
                section, topic, filename))
        else:
            # file found, adding new topic
            toggles[topic] = default_topicblock
            with open(filename, 'w') as outfile:
                json.dump(toggles, outfile)
                outfile.close()

            topicblock = default_topicblock
            srv.logging.debug('togglestate() was called from the {} section, did not find {} in {}'.format(
                section, topic, filename))
            srv.logging.debug('togglestate() added {} to {} with blocking set to {}'.format(
                topic, filename, topicblock))

    except Exception as e:
        # file not found or other error
        topicblock = default_topicblock
        srv.logging.debug('togglestate() encountered an error: {}'.format(e))

    srv.logging.debug('togglestate() will return {}'.format(topicblock))
    return topicblock

import time
import copy
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
	        srv.logging.debug('togglestate() was called from the ' + section + ' section and found ' + topic + ' in ' + filename)
        else:
            # file found, adding new topic
            toggles[topic] = default_topicblock
            with open(filename, 'w') as outfile:
                json.dump(toggles, outfile)
                outfile.close()

            topicblock = default_topicblock
            srv.logging.debug('togglestate() was called from the ' + section + ' section, did not find ' + topic + ' in ' + filename
)
            srv.logging.debug('togglestate() added ' + topic + ' to ' + filename + ' with blocking set to ' + str(topicblock))

    except Exception as e:
        # file not found or other error
        topicblock = default_topicblock
        srv.logging.debug('togglestate() encountered an error: ' + str(e) )

    srv.logging.debug('togglestate() will return ' + str(topicblock))
    return topicblock

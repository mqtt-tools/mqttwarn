# -*- coding: utf-8 -*-
# mqttwarn example function extensions
import time
import copy

try:
    import json
except ImportError:
    import simplejson as json

def OwnTracksTopic2Data(topic):
    if type(topic) == str:
        try:
            # owntracks/username/device
            parts = topic.split('/')
            username = parts[1]
            deviceid = parts[2]
        except:
            deviceid = 'unknown'
            username = 'unknown'
        return dict(username=username, device=deviceid)
    return None

def OwnTracksConvert(data):
    if type(data) == dict:
        # Better safe than sorry: Clone transformation dictionary to prevent leaking local modifications
        # See also https://github.com/jpmens/mqttwarn/issues/219#issuecomment-271815495
        data = copy.copy(data)
        tst = data.get('tst', int(time.time()))
        data['tst'] = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(tst)))
        # Remove these elements to eliminate warnings
        for k in ['_type', 'desc']:
            data.pop(k, None)

        return "{username} {device} {tst} at location {lat},{lon}".format(**data)

# custom function to filter out any OwnTracks notifications which do
# not contain the 'batt' parameter
def OwnTracksBattFilter(topic, message):
    data = dict(json.loads(message).items())
    if 'batt' in data:
        if data['batt'] is not None:
            return int(data['batt']) > 20

    return True     # Suppress message because no 'batt'

def TopicTargetList(topic=None, data=None, srv=None):
    """
    Custom function to compute list of topic targets based on MQTT topic and/or transformation data.
    Obtains MQTT topic, transformation data and service object.
    Returns list of topic target identifiers.
    """

    # optional debug logger
    if srv is not None:
        srv.logging.debug('topic={topic}, data={data}, srv={srv}'.format(**locals()))

    # Use a fixed list of topic targets for demonstration purposes.
    targets = ['log:debug']

    # In the real world, you would compute proper topic targets based on information
    # derived from transformation data, which in turn might have been enriched
    # by ``datamap`` or ``alldata`` transformation functions before, like that:
    if 'condition' in data:

        if data['condition'] == 'sunny':
            targets.append('file:mqttwarn')

        elif data['condition'] == 'rainy':
            targets.append('log:warn')

    return targets

def PushoverAddImageUrl(data=None, srv=None):
    #formatting method to create a new payload for the pushpver service
	#which will use zone information from the mqtt topic and utilise an image
	#url to post an image when a particular mqtt message is found.
	
    text = "unknown"
    if data is not None and type(data) == dict:
       data = copy.copy(data)
       if srv is not None:
          srv.logging.debug('Data retrieved and is in dict format')
          srv.logging.debug(data)
       text = data['payload']  
       topic = data['topic']
    else:
       if srv is not None:
           srv.logging.debug('Data retrieved and is in message format')
       if data is not None:
           text = data

    parts = topic.split('/')
    zone = parts[2]

    if srv is not None:
       srv.logging.debug('Topic {0} and so zone is {1}'.format(topic,zone))

    if zone == 'artbitary mqtt parm':
	   #url from dlink camera, replace with 
       url = "http://192.168.0.100/image.jpg"
    
	
    payload = {
         'message':  'ALERT {0} being Opened/Closed'.format(zone),
         'imageurl': url
    }

    if srv is not None:
        srv.logging.debug('New payload constructed:')
        srv.logging.debug(json.dumps(payload))

    return json.dumps(payload)
	
def publish_public_ip_address(srv=None):
    """
    Custom function used as a periodic task for publishing your public ip address to the MQTT bus.
    Obtains service object.
    Returns None.
    """

    import socket
    import requests

    hostname = socket.gethostname()
    ip_address = requests.get('https://httpbin.org/ip').json().get('origin')

    if srv is not None:

        # optional debug logger
        srv.logging.debug('Publishing public ip address "{ip_address}" of host "{hostname}"'.format(**locals()))

        # publish ip address to mqtt
        srv.mqttc.publish('test/ip/{hostname}'.format(**locals()), ip_address)

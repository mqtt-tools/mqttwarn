import time

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

def TopicTargetList(topic=None, payload=None, data=None, srv=None):
    """
    Custom function to compute list of topic subscription
    targets based on topic and/or transformation data.
    Pass MQTT topic, transformation data, service object
    and optionally raw message payload.
    """
    if srv is not None:
        srv.logging.debug('topic={topic}, payload={payload}, data={data}, srv={srv}'.format(**locals()))

    # Use a fixed list of topic subscription targets for demonstration purposes.
    # In the real world, you would look up proper targets based on information
    # derived from transformation data, which in turn might have been enriched
    # by ``datamap`` or ``alldata`` transformation functions before.
    targets = ['foo:bar', 'log:info', 'file:mqttwarn']

    return targets

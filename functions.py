import logging
import time

# Need JSON for OwnTracks battery filter
try:
    import json
except ImportError:
    import simplejson as json

# Need URLLIB for geo lookups
from urllib import urlencode
from urllib2 import urlopen

# custom function to extract the 'username' from the OwnTracks topic
def owntracks_data(topic):
    if type(topic) == str:
        try:
            # /owntracks/username
            parts = topic.split('/')
            username = parts[2].capitalize()
        except:
            username = 'Unknown'
        return dict(username=username)
    return None

# custom function to filter out any OwnTracks notifications which are
# not 'event' type publishes - i.e. standard location updates etc
def owntracks_eventfilter(topic, message):
    data = dict(json.loads(message).items())
    return 'event' not in data

# custom function to filter out any OwnTracks notifications which do
# not contain the 'batt' parameter
def owntracks_battfilter(topic, message):
    data = dict(json.loads(message).items())
    if 'batt' in data:
        return int(data['batt']) > 20
    return True

# custom function to filter out any OwnTracks notifications which do
# not contain the 'lat' parameter
def owntracks_geofilter(topic, message):
    data = dict(json.loads(message).items())
    return 'lat' not in data

# this function will reverse geo the address and return a formatted string
def owntracks_geolookup(data):
    if type(data) == dict:
        # Remove these elements to eliminate warnings
        for k in ['_type', 'desc']:
            data.pop(k, None)
        whereisthis = getaddress(data)
        data['whereisthis'] = whereisthis
        return "{username} was last seen at {whereisthis}".format(**data)
    return "Unable to lookup the address for {username}"

class ReverseGeo(object):
    """
    Reverse geocoder using the MapQuest Open Platform Web Service.
    """
 
    def __init__(self):
        """Initialize reverse geocoder; no API key is required by the
           Nomatim-based platform"""
        self.url = "http://open.mapquestapi.com/nominatim/v1/reverse?format=json&addressdetails=1&%s"
    
    def parse_json(self, data):
        try:
            data = json.loads(data)
        except:
            data = {}
        return data
 
    def reverse(self, lat, lon):
        params = { 'lat': lat, 'lon' : lon }
        url = self.url % urlencode(params)
        data = urlopen(url)
        response = data.read()
        return self.parse_json(response)
 
def getaddress(data):
    if type(data) == dict and 'lat' in data:        
        nominatim = ReverseGeo()
        lookitup = nominatim.reverse(data['lat'], data['lon'])
        logging.debug(lookitup)
        fulladdress = lookitup['display_name']
        return str(fulladdress)
    return None

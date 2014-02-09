
broker = 'localhost'
port = 1883
username = None
password = None

# Pushover.net keys
userkey = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

# Map MQTT topics (wildcards allowed!) to Pushover.net app keys
topicmap = {
    'home/events/owntracks/+/+' : 'yyyyyyyyyyyyyyyyyyyyyyyyyyyyyy', # owntracks
    'home/t1'                   : 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzz', # icinga
    'oh/#'                      : 'mmmmmmmmmmmmmmmmmmmmmmmmmmmmmm', # openhab
}



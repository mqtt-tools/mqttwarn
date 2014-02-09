
broker = 'localhost'
port = 1883
username = None
password = None

# Pushover.net User Key (on top right of their control panel)
userkey = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

# Map MQTT topics (wildcards allowed!) to Pushover.net app keys
# (also called API Token/Key)
topicmap = {
    'home/events/owntracks/+/+' : 'yyyyyyyyyyyyyyyyyyyyyyyyyyyyyy', # owntracks
    'home/t1'                   : 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzz', # icinga
    'oh/#'                      : 'mmmmmmmmmmmmmmmmmmmmmmmmmmmmmm', # openhab
}



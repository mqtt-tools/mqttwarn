
broker = 'localhost'
port = 1883
username = None
password = None

logfile = 'logfile'

# Pushover.net User Key (on top right of their control panel)
userkey = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

# Define additional user keys for further pushover accounts

second_key = '00000000000000000000000000000'

# Map MQTT topics (wildcards allowed!) to Pushover.net app keys
# (also called API Token/Key)
#
# If the right-hand-side (rhs) is a string, that appkey will be used for
# messages for that topic. If it is a dict, use that userkey and that appkey
# for this particular topic

topicmap = {
    'home/events/owntracks/+/+' : 'yyyyyyyyyyyyyyyyyyyyyyyyyyyyyy', # owntracks
    'home/t1'                   : 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzz', # icinga
    'oh/#'                      : 'mmmmmmmmmmmmmmmmmmmmmmmmmmmmmm', # openhab

     # for the `announce/+' topic, use the specified userkey/appkey
    'announce/+'                : { 'userkey' : second_key,
                                    'appkey'  : 'oooooooooooooooooooooooooooooo' }, # second's account
}



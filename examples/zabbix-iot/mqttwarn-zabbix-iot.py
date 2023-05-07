def decode_for_zabbix(topic, data, srv=None):
    status_key = None

    # the first part (part[0]) is always tele
    # the second part (part[1]) is the device, the value comes from
    # the third part (part[2]) is the name of the metric (e.g. temperature/humidity/voltage...)
    parts = topic.split('/')
    client = parts[1]
    key = parts[2]

    return dict(client=client, key=key, status_key=status_key)

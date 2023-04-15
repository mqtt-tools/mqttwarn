# OwnTracks » Low-battery warnings


## About

By subscribing to your [OwnTracks] topic and adding the following custom filter
you can get `mqttwarn` to send notifications when your phone battery gets below 
a certain level.


## Implementation

```python
import json

def owntracks_batteryfilter(topic: str, message: str):
    data = dict(json.loads(message).items())
    if data["batt"] is not None:
        return int(data["batt"]) > 20
    return True
```

Now, simply add your choice of target(s) to the [topic section](#topics), and a
corresponding format string, and you are done.
```ini
[owntracks/#]
targets = pushover, xbmc
filter = owntracks_batteryfilter()
format = My phone battery is getting low ({batt}%)!
```


[OwnTracks]: https://owntracks.org

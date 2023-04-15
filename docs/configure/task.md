(task)=
(tasks)=
# Tasks


## Periodic tasks

_mqttwarn_ can use functions you define in the file specified `[defaults]` section
to periodically do whatever you want, for example, publish an MQTT message. There
are two things you have to do:

1. Create the function
2. Configure _mqttwarn_ to use that function and specify the interval in seconds

Assume we have the following user-defined function.
```python
from mqttwarn.model import Service

def pinger(srv: Service):
    srv.mqttc.publish("pt/PINGER", "Hello from mqttwarn!", qos=0)
```

We configure this function to run every, say, 10 seconds, in the `mqttwarn.ini`,
in the `[cron]` section:

```ini
[cron]
pinger = 10.5
```

Each keyword in the `[cron]` section specifies the name of one of your custom
functions, and its float value is an interval in _seconds_ after which your
user-defined function, in this case `pinger()`, is invoked. Your function has
access to the `srv` object described above.

Function names are to be specified in lower-case characters.

If you want to run the user-defined function immediately after starting mqttwarn
instead of waiting for the interval to elapse, you might want to add `now=true`.
```ini
[cron]
pinger = 10.5; now=true
```

import warnings

from mqttwarn.services.apprise_single import plugin

warnings.warn("`mqttwarn.services.apprise` will be removed in a future release of mqttwarn. "
              "Please use `mqttwarn.services.apprise_single` or `mqttwarn.services.apprise_multi` instead.",
              category=DeprecationWarning)

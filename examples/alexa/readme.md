# Amazon Alexa

## About

An alternative to alexa-notify-me notification (speaker glows yellow and awaits
instruction to play the notification) is for TTS to specific devices or 
announce to a speaker group.

See the examples directory for integration with pipe and the [alexa-remote-control]
shell scripts.

## Instructions

* Download or clone [alexa-remote-control].
* Edit the [secrets.sh](./secrets.sh) file.
* Ensure paths are correct.
  Scripts and `alexa.ini` file assume path `/home/pi/shell/alexa-remote-control`.
* Edit `alexa.ini` file targets with device names and/or group name.
  `stdin` for single devices, `announce_stdin` for groups.
* Sanity check, `chmod a+x` on all shell scripts.


[alexa-remote-control]: https://github.com/thorsten-gehrig/alexa-remote-control

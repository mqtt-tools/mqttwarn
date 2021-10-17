import shlex
import sys

import pytest
from mqttwarn.commands import run


def test_command_dump_config(capfd):

    command = "mqttwarn make-config"
    stdout, stderr = invoke_command(capfd, command)
    assert 'mqttwarn example configuration file "mqttwarn.ini"' in stdout, stdout


def test_command_dump_samplefuncs(capfd):

    command = "mqttwarn make-samplefuncs"
    stdout, stderr = invoke_command(capfd, command)
    assert "# mqttwarn example function extensions" in stdout, stdout


def test_command_standalone_plugin(capfd, caplog):

    # FIXME: Make it work on Windows.
    if sys.platform.startswith("win"):
        raise pytest.xfail("Skipping test, fails on Windows")

    command = [
        "mqttwarn",
        "--plugin=log",
        """--options={"message": "Hello world", "addrs": ["crit"]}""",
    ]
    stdout, stderr = invoke_command(capfd, command)

    assert """Running service plugin "log" with options""" in caplog.text
    assert 'Successfully loaded service "log"' in caplog.messages
    assert "Hello world" in caplog.messages
    assert "Plugin response: True" in caplog.messages


def invoke_command(capfd, command):
    if not isinstance(command, list):
        command = shlex.split(command)
    sys.argv = command
    print("sys.argv:", sys.argv)
    run()
    stdouterr = capfd.readouterr()
    stdout = stdouterr.out
    stderr = stdouterr.err
    return stdout, stderr

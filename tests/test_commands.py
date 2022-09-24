import os
import sys
from unittest.mock import patch

import pytest
from tests.util import invoke_command


def test_mqttwarn_main(capsys):
    """
    Test the `mqttwarn.__main__` module.
    """
    with patch("sys.argv", "mqttwarn -h"):
        with pytest.raises(SystemExit):
            import mqttwarn.__main__  # noqa:F401
    assert "Usage:" in capsys.readouterr().out


def test_command_dump_config(mqttwarn_bin, capfd):

    command = f"{mqttwarn_bin} make-config"
    stdout, stderr = invoke_command(capfd, command)

    os.system(command)
    stdout = capfd.readouterr().out

    assert 'mqttwarn example configuration file "mqttwarn.ini"' in stdout, stdout


def test_command_dump_samplefuncs(mqttwarn_bin, capfd):

    command = f"{mqttwarn_bin} make-samplefuncs"
    stdout, stderr = invoke_command(capfd, command)
    assert "# mqttwarn example function extensions" in stdout, stdout

    os.system(command)
    stdout = capfd.readouterr().out

    assert "# mqttwarn example function extensions" in stdout, stdout


def test_command_standalone_plugin(mqttwarn_bin, capfd, caplog):

    # FIXME: Make it work on Windows.
    if sys.platform.startswith("win"):
        raise pytest.xfail("Skipping test, fails on Windows")

    command = [
        mqttwarn_bin,
        "--plugin=log",
        """--options={"message": "Hello world", "addrs": ["crit"]}""",
    ]
    stdout, stderr = invoke_command(capfd, command)

    assert """Running service plugin "log" with options""" in caplog.text
    assert 'Successfully loaded service "log"' in caplog.messages
    assert "Hello world" in caplog.messages
    assert "Plugin response: True" in caplog.messages


def test_command_dump_config_real(mqttwarn_bin, capfd):
    """
    Proof that the configuration scaffolding will write files with UTF-8 encoding on all platforms.
    """

    try:
        command = f"{mqttwarn_bin} make-config > foobar.ini"
        exitcode = os.system(command) % 255
        assert exitcode == 0, f"Invoking command '{command}' failed"

        ini_content = open("foobar.ini", encoding="utf-8").read()
        assert 'mqttwarn example configuration file "mqttwarn.ini"' in ini_content

    finally:
        os.unlink("foobar.ini")

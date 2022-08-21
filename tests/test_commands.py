import os
import shlex
import shutil
import sys

import pytest
from mqttwarn.commands import run


def test_command_dump_config(capfd):

    command = f"{find_mqttwarn()} make-config"
    stdout, stderr = invoke_command(capfd, command)

    os.system(command)
    stdout = capfd.readouterr().out

    assert 'mqttwarn example configuration file "mqttwarn.ini"' in stdout, stdout


def test_command_dump_samplefuncs(capfd):

    command = f"{find_mqttwarn()} make-samplefuncs"
    stdout, stderr = invoke_command(capfd, command)
    assert "# mqttwarn example function extensions" in stdout, stdout

    os.system(command)
    stdout = capfd.readouterr().out

    assert '# mqttwarn example function extensions' in stdout, stdout


def test_command_standalone_plugin(capfd, caplog):

    # FIXME: Make it work on Windows.
    if sys.platform.startswith("win"):
        raise pytest.xfail("Skipping test, fails on Windows")

    command = [
        find_mqttwarn(),
        "--plugin=log",
        """--options={"message": "Hello world", "addrs": ["crit"]}""",
    ]
    stdout, stderr = invoke_command(capfd, command)

    assert """Running service plugin "log" with options""" in caplog.text
    assert 'Successfully loaded service "log"' in caplog.messages
    assert "Hello world" in caplog.messages
    assert "Plugin response: True" in caplog.messages


def test_command_dump_config_real(capfd):
    """
    Proof that the configuration scaffolding will write files with UTF-8 encoding on all platforms.
    """

    try:
        command = f"{find_mqttwarn()} make-config > foobar.ini"
        exitcode = os.system(command) % 255
        assert exitcode == 0, f"Invoking command '{command}' failed"

        ini_content = open("foobar.ini", encoding="utf-8").read()
        assert 'mqttwarn example configuration file "mqttwarn.ini"' in ini_content

    finally:
        os.unlink("foobar.ini")


def find_mqttwarn():
    """
    Find `mqttwarn` executable, located within the inline virtualenv.
    """

    path_candidates = [None, ".venv/bin", r".venv\Scripts"]
    for path_candidate in path_candidates:
        mqttwarn_bin = shutil.which("mqttwarn", path=path_candidate)
        if mqttwarn_bin is not None:
            return mqttwarn_bin

    raise FileNotFoundError(f"Unable to discover 'mqttwarn' executable within {path_candidates}")


def invoke_command(capfd, command):
    if not isinstance(command, list):
        command = shlex.split(command)
    sys.argv = command
    run()
    stdouterr = capfd.readouterr()
    stdout = stdouterr.out
    stderr = stdouterr.err
    return stdout, stderr

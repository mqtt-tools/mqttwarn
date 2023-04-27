# -*- coding: utf-8 -*-
# (c) 2018-2022 The mqttwarn developers
import os
import sys
from unittest import mock
from unittest.mock import Mock, patch

import docopt
import pytest

import mqttwarn.commands
from mqttwarn.configuration import Config
from tests.util import invoke_command


def test_mqttwarn_main_void(capsys):
    """
    Test the `mqttwarn.__main__` module.
    """
    with patch("sys.argv", "foobar"):
        with pytest.raises(docopt.DocoptExit) as ex:
            import mqttwarn.__main__  # noqa:F401
        assert ex.match("Usage:")


def test_mqttwarn_main_help(capsys):
    """
    Test the `mqttwarn.__main__` module with the `-h` option.
    """
    with patch("sys.argv", ["mqttwarn", "-h"]):
        with pytest.raises(SystemExit):
            import mqttwarn.__main__  # noqa:F401
    assert "Usage:" in capsys.readouterr().out


def test_run_mqttwarn_with_configuration_from_environment(mocker, caplog):
    """
    Verify that `mqttwarn.commands.run_mqttwarn` works as expected.
    Here, a configuration file is obtained using the `MQTTWARNINI` environment variable.
    """
    mocker.patch("os.environ", {"MQTTWARNINI": "tests/etc/no-functions.ini"})
    mocker.patch("sys.argv", ["mqttwarn"])
    mocker.patch("mqttwarn.commands.subscribe_forever")
    mqttwarn.commands.run_mqttwarn()

    assert caplog.messages == [
        "Starting mqttwarn",
        "Log level is DEBUG",
    ]


def test_run_mqttwarn_with_configuration_from_file(mocker, caplog):
    """
    Verify that `mqttwarn.commands.run_mqttwarn` works as expected.
    Here, a configuration file is obtained using the `--config-file` command line option.
    """
    mocker.patch("sys.argv", ["mqttwarn-custom"])
    mocker.patch("mqttwarn.commands.subscribe_forever")
    mqttwarn.commands.run_mqttwarn(configfile="tests/etc/no-functions.ini")

    assert caplog.messages == [
        "Starting mqttwarn-custom",
        "Log level is DEBUG",
    ]


def test_run_command(mocker, caplog):
    """
    Verify that `mqttwarn.commands.run` works as expected.
    """
    mocker.patch("sys.argv", ["mqttwarn"])
    run_mqttwarn: Mock = mocker.patch("mqttwarn.commands.run_mqttwarn")
    mqttwarn.commands.run()

    run_mqttwarn.assert_called_once()
    assert caplog.messages == []


def test_command_dump_config(mqttwarn_bin, capfd):
    """
    Verify that `mqttwarn make-config` works as expected.
    """

    command = f"{mqttwarn_bin} make-config"
    stdout, stderr = invoke_command(capfd, command)

    os.system(command)
    stdout = capfd.readouterr().out

    assert 'mqttwarn example configuration file "mqttwarn.ini"' in stdout, stdout


def test_command_dump_udf(mqttwarn_bin, capfd):
    """
    Verify that `mqttwarn make-udf` works as expected.
    """

    command = f"{mqttwarn_bin} make-udf"
    stdout, stderr = invoke_command(capfd, command)
    assert "# mqttwarn example function extensions" in stdout, stdout

    os.system(command)
    stdout = capfd.readouterr().out

    assert "# mqttwarn example function extensions" in stdout, stdout


def test_command_standalone_plugin(mqttwarn_bin, capfd, caplog):
    """
    Verify that invoking a plugin standalone from the command line works.
    """

    # FIXME: Make it work on Windows.
    if sys.platform.startswith("win"):
        raise pytest.xfail("Skipping test, fails on Windows")

    command = [
        mqttwarn_bin,
        "--plugin=log",
        """--options={"message": "Hello world", "addrs": ["crit"]}""",
        """--config={"foo": "bar"}""",
    ]
    stdout, stderr = invoke_command(capfd, command)

    assert 'Running service plugin "log" with options' in caplog.text
    assert 'Successfully loaded service "log"' in caplog.messages
    assert "Hello world" in caplog.messages
    assert "Plugin response: True" in caplog.messages


def test_command_standalone_plugin_with_configfile(mqttwarn_bin, tmp_path, capfd, caplog):
    """
    Verify that invoking a plugin standalone from the command line works.
    This time, also use a `--config-file` option.
    """

    # FIXME: Make it work on Windows.
    if sys.platform.startswith("win"):
        raise pytest.xfail("Skipping test, fails on Windows")

    ini_file = tmp_path.joinpath("empty.ini")
    ini_file.touch()

    command = [
        mqttwarn_bin,
        "--plugin=log",
        f"--config-file={ini_file}",
        '--config={"foo": "bar"}',
        '--options={"message": "Hello world", "addrs": ["crit"]}',
    ]
    stdout, stderr = invoke_command(capfd, command)

    assert """Running service plugin "log" with options""" in caplog.text
    assert 'Successfully loaded service "log"' in caplog.messages
    assert "Hello world" in caplog.messages
    assert "Plugin response: True" in caplog.messages


def test_command_dump_config_real(mqttwarn_bin, tmp_path, capfd):
    """
    Proof that the configuration scaffolding will write files with UTF-8 encoding on all platforms.
    """

    ini_file = tmp_path.joinpath("testdrive.ini")

    command = f"{mqttwarn_bin} make-config > {ini_file}"
    exitcode = os.system(command) % 255
    assert exitcode == 0, f"Invoking command '{command}' failed"

    ini_content = open(ini_file, encoding="utf-8").read()
    assert 'mqttwarn example configuration file "mqttwarn.ini"' in ini_content


def test_setup_logging_default(mocker):
    """
    Verify the default behavior of the `setup_logging` function.
    """
    config = Config()

    logging_mock: Mock = mocker.patch("logging.basicConfig")
    mqttwarn.commands.setup_logging(config)
    logging_mock.assert_called_with(
        format="%(asctime)-15s %(levelname)-8s [%(name)-26s] %(message)s", level=10, stream=mock.ANY
    )


def test_setup_logging_no_logfile():
    """
    Verify the behavior of the `setup_logging` function, when the `logfile` setting is empty.
    """
    config = Config()
    config.logfile = ""
    mqttwarn.commands.setup_logging(config)


def test_setup_logging_logfile_without_protocol(mocker):
    """
    Verify the behavior of the `setup_logging` function, when the `logfile` setting is given without protocol.
    """
    config = Config()
    config.logfile = "sys.stderr"

    logging_mock: Mock = mocker.patch("logging.basicConfig")
    mqttwarn.commands.setup_logging(config)
    logging_mock.assert_called_with(
        filename="sys.stderr", format="%(asctime)-15s %(levelname)-8s [%(name)-26s] %(message)s", level=10
    )

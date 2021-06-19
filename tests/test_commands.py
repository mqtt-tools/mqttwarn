import os


def test_command_dump_config(capfd):

    command = "mqttwarn make-config"

    os.system(command)
    stdout = capfd.readouterr().out

    assert 'mqttwarn example configuration file "mqttwarn.ini"' in stdout, stdout


def test_command_dump_samplefuncs(capfd):

    command = "mqttwarn make-samplefuncs"

    os.system(command)
    stdout = capfd.readouterr().out

    assert '# mqttwarn example function extensions' in stdout, stdout


def test_command_standalone_plugin(capfd):

    command = """mqttwarn --plugin=log --options='{"message": "Hello world", "addrs": ["crit"]}'"""

    os.system(command)
    stderr = capfd.readouterr().err

    assert 'Successfully loaded service "log"' in stderr, stderr
    assert 'Hello world' in stderr, stderr
    assert 'Plugin response: True' in stderr, stderr

from unittest.mock import patch

from mova.utils.system import run_command


def test_run_command_rejects_shell_string_before_starting_process():
    with patch("mova.utils.system.subprocess.Popen") as popen:
        result = run_command("echo safe", allowed_commands={"echo"})
    assert result[0] == -1
    assert "argv" in result[2]
    popen.assert_not_called()


def test_run_command_rejects_unapproved_executable_before_starting_process():
    with patch("mova.utils.system.subprocess.Popen") as popen:
        result = run_command(["id"], allowed_commands={"echo"})
    assert result == (-1, "", "Command 'id' is not allowed")
    popen.assert_not_called()


def test_run_command_uses_allowlisted_argv_without_shell():
    with patch("mova.utils.system.subprocess.Popen") as popen:
        popen.return_value.communicate.return_value = ("ok\\n", "")
        popen.return_value.returncode = 0
        result = run_command(["echo", "ok"], allowed_commands={"echo"})
    assert result == (0, "ok\\n", "")
    popen.assert_called_once_with(
        ["echo", "ok"], stdout=-1, stderr=-1, text=True,
    )

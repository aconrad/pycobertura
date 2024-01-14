import mock
import runpy


def test_cli():
    with mock.patch("click.CommandCollection") as mock_cli:
        runpy.run_module("pycobertura", run_name="__main__")

    mock_cli.assert_called_once()
    mock_cli.return_value.assert_called_once_with()

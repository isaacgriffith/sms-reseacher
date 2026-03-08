"""Unit tests for agent-eval CLI help output."""

from typer.testing import CliRunner

from agent_eval.cli import app

runner = CliRunner()


class TestCliHelp:
    """Tests for agent-eval CLI top-level help."""

    def test_help_exits_zero(self) -> None:
        """agent-eval --help exits with code 0."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0

    def test_help_contains_evaluate(self) -> None:
        """Help output lists the evaluate command."""
        result = runner.invoke(app, ["--help"])
        assert "evaluate" in result.output

    def test_help_contains_report(self) -> None:
        """Help output lists the report command."""
        result = runner.invoke(app, ["--help"])
        assert "report" in result.output

    def test_help_contains_compare(self) -> None:
        """Help output lists the compare command."""
        result = runner.invoke(app, ["--help"])
        assert "compare" in result.output

    def test_help_contains_improve(self) -> None:
        """Help output lists the improve command."""
        result = runner.invoke(app, ["--help"])
        assert "improve" in result.output

    def test_version_flag_exits_zero(self) -> None:
        """agent-eval --version exits with code 0."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0

    def test_version_output(self) -> None:
        """agent-eval --version prints version string."""
        result = runner.invoke(app, ["--version"])
        assert "0.1.0" in result.output

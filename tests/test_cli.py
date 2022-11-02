""" Test for rocks CLI commands."""
from click.testing import CliRunner

from rocks import cli

# See https://click.palletsprojects.com/en/7.x/testing/

# Known subcommands are
# - identify
# - id
# - docs
# - info
# - status
# - properties
# - update

# Unknow is any property command, eg
# - osculating_elements.semi_major_axis
# - albedo
# - taxonomies


def test_identify():
    """Identify should retrun number and name."""
    runner = CliRunner()
    result = runner.invoke(cli.cli_rocks, ["identify", "Massalia"])
    assert result.output == "(20) Massalia\n"


def test_id():
    """id is alias of identify."""
    runner = CliRunner()
    result = runner.invoke(cli.cli_rocks, ["id", "Massalia"])
    assert result.output == "(20) Massalia\n"


def test_info():
    """Info display."""
    runner = CliRunner()
    result = runner.invoke(cli.cli_rocks, ["info", "Massalia"])
    assert result.exit_code == 0


def test_albedo():
    """Albedo display."""
    runner = CliRunner()
    result = runner.invoke(cli.cli_rocks, ["albedo", "10"])
    assert "+-" in result.output  # should ensure that there is a value +- error


#  def test_taxonomy():
#  """Get taxonomic class. """
#  runner = CliRunner()
#  result = runner.invoke(cli.cli_rocks, ["taxonomy.class_", "Massalia"])
#  assert result.output == "S"

#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Author: Max Mahlke
    Date: 29 May 2020

    Test for rocks CLI commands

    Call as:	python test_cli.py
'''
from click.testing import CliRunner

from rocks import cli

# See https://click.palletsprojects.com/en/7.x/testing/


def test_identify():
    runner = CliRunner()
    result = runner.invoke(cli.cli_rocks, ['identify', 'Massalia'])
    assert result.output == '(20) Massalia\n'


def test_info():
    runner = CliRunner()
    result = runner.invoke(cli.cli_rocks, ['info', 'Massalia'])
    assert result.exit_code == 0


def test_taxonomy():
    runner = CliRunner()
    result = runner.invoke(cli.cli_rocks, ['taxonomy', 'Massalia'])
    assert result.output == 'S'


def test_albedo():
    runner = CliRunner()
    result = runner.invoke(cli.cli_rocks, ['albedo', 'Massalia'])
    assert result.exit_code == 0

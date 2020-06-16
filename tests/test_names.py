#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Author: Max Mahlke
    Date: 27 May 2020

    Unit tests for names module
'''
import numpy as np
import pandas as pd
import pytest

from rocks import names

# First value is input identifier, tuple is the expected
# response, boolean is True if local lookup, False if quaero
IDS_RESULTS_LOCAL = [
    [19, ('Fortuna', 19), True],
    ['192', ('Nausikaa', 192), True],
    ['eos', ('Eos', 221), True],
    ['SCHWARTZ', ('Schwartz', 13820), True],
    ["G!kun||'homdima", ("G!kun||'homdima", 229762), True],
    ['1290 T-1', ('1290 T-1', 12946), True],
    ['1290_T-1', ('1290 T-1', 12946), True],
    ['P/PANSTARRS', ('P/2014 M4', np.nan), False],
    ['1950 RW', ('Gyldenkerne', 5030), False],
    ['2001je2', ('2001 JE2', 131353), True],
    ['2001_JE2', ('2001 JE2', 131353), True],
    ['2010 OR', ('2010 OR', np.nan), False],
    ['2014_ye64', ('2014 YE64', 545135), True],
    ['2004BQ102', ('2004 BQ102', 450274), True],
    ['A999AB2', ('1999 AB2', 53103), True],
    [9e7, (np.nan, np.nan), False],
    [None, (np.nan, np.nan), True],
]

SSO_IDS = [it[0] for it in IDS_RESULTS_LOCAL]
EXPECTED = [it[1] for it in IDS_RESULTS_LOCAL]
LOCAL = [it[2] for it in IDS_RESULTS_LOCAL]


@pytest.mark.parametrize('id_, expected', zip(SSO_IDS, EXPECTED), ids=str)
def test_single_identifiers(id_, expected):
    '''Common-case lookups of single SSO ids'''
    name, number = names.get_name_number(id_)
    np.testing.assert_equal((name, number), expected)


@pytest.mark.parametrize('ids',
                         [SSO_IDS, np.array(SSO_IDS), pd.Series(SSO_IDS)],
                         ids=['list', 'array', 'series'])
def test_many_identifiers(ids):
    '''Common-case lookups of many SSO ids, passed as list, array, Series'''
    results = names.get_name_number(ids, progress=False)
    np.testing.assert_equal(results, EXPECTED)


@pytest.mark.parametrize('ncores', [1, 2])
def test_parallelization(ncores):
    '''Run with different number of cores'''
    results = names.get_name_number(SSO_IDS, parallel=ncores)
    np.testing.assert_equal(results, EXPECTED)


@pytest.mark.parametrize('id_, filename', [('2012 P-L', '2012P-L')])
def test_filenames(id_, filename):
    '''Run with different number of cores'''
    fn = names.to_filename(id_)
    assert fn == filename


@pytest.mark.parametrize('id_, expected, local', IDS_RESULTS_LOCAL[:-1])
def test_local_vs_remote(id_, expected, local, monkeypatch):
    '''Ensure that queries which can be resolved locally are run locally'''

    # Mock return for quaero query
    def mockreturn(sso, verbose):
        return False

    monkeypatch.setattr(names, '_query_quaero', mockreturn)

    result = names.get_name_number(id_, progress=False, parallel=1)

    if local:
        assert result == expected
    else:
        assert result is False

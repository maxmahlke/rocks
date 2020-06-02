#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Author: Max Mahlke
    Date: 27 May 2020

    Unit tests for properties module
'''
import numpy as np
import pytest

from rocks import properties

SSO_IDS = [
    19,
    '192',
    'eos',
    'SCHWARTZ',
    "G!kun||'homdima",
    '1290 T-1',
    'P/PANSTARRS',
    '1950 RW',
    '2001je2',
    '2001_JE2',
    '2010 OR',
    '2004BQ102',
    'A999AB2',
    9e7,
]


EXPECTED_CLASS_COMPLEX = [
    ('Ch'),
    ('Sw'),
    ('K'),
    ('B'),
    (np.nan),
    (np.nan),
    (np.nan),
    (np.nan),
    ('CX'),
    ('CX'),
    (np.nan),
    ('C'),
    ('C'),
    (np.nan)
]


@pytest.mark.parametrize('id_, expected', zip(SSO_IDS, EXPECTED_CLASS_COMPLEX),
                         ids=str)
def test_taxonomy_single_identifiers(id_, expected):
    '''Common-case lookups of single SSO ids'''
    class_, _ = properties.get_taxonomy(id_)
    np.testing.assert_equal(class_, expected)


def test_many_identifiers():
    '''Common-case lookups of many SSO ids, passed as list'''
    results = properties.get_property('taxonomy', SSO_IDS)
    results = [r[0] for r in results]
    np.testing.assert_equal(results, EXPECTED_CLASS_COMPLEX)


# @pytest.mark.parametrize('ncores', [1, 2])
# def test_parallelization(ncores):
    # '''Run with different number of cores'''
    # results = names.get_name_number(SSO_IDS, parallel=ncores)
    # np.testing.assert_equal(results, EXPECTED)

# def test_local_lookups():
    # '''Identifiers which should always be found locally'''
    # assert names.get_name_number(19) == ('Fortuna', 19)


# def test_quaero_lookups():
    # '''Identifiers which should always be queried from quaero'''
    # assert names.get_name_number(19) == ('Fortuna', 19)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Author: Max Mahlke
    Date: 09 June 2020

    Tests the rocks tools module

    Call as:	pytest test_tools.py
'''
import pytest

from rocks import tools


import pandas as pd
url = 'https://www.minorplanetcenter.net/iau/lists/NumberedMPs.txt'

data = pd.read_fwf(url, colspecs=[(0, 7), (9, 29), (29, 41)],
                   names=['number', 'name', 'designation'],
                   converters={'number': lambda x: int(x.replace('(', ''))},
                   dtype={'name': str})
data['name'] = data['name'].fillna(data.designation)
print(data.describe())
print(data.head)

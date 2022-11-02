#!/usr/bin/env python
"""Utility functions for rocks."""

from bs4 import BeautifulSoup
from functools import reduce
import json
import re
import shutil
import string
import tarfile
import urllib

import numpy as np
import Levenshtein as lev
import requests
import rich
from rich.progress import track

from rocks import (
    config,
    datacloud,
    identify,
    index,
    resolve,
    ssodnet,
)

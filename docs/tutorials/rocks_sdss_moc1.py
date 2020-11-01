#!/usr/bin/env python

"""Identify objects in SDSS Moving-Objects Catalogue DR1 with rocks."""

import numpy as np
import pandas as pd
import rocks

# ------
# Download SDSS MOC1 (6.2MB)
data = pd.read_fwf(
    "https://faculty.washington.edu/ivezic/sdssmoc/ADR1.dat.gz",
    colspecs=[(244, 250), (250, 270)],
    names=["numeration", "designation"],
)

print(f"Number of observations in SDSS MOC1: {len(data)}")

# Remove the unknown objects
data = data[data.designation.str.strip(" ") != "-"]
print(f"Observations of known objects: {len(set(data.designation))}")

# ------
# Get current designations and numbers for objects

# Unnumbered objects should be NaN
data.loc[data.numeration == 0, "numeration"] = np.nan

# Create list of identifiers by merging 'numeration' and 'designation' columns
ids = data.numeration.fillna(data.designation)
print("Identifying known objects in catalogue..")
names_numbers = rocks.identify(ids)

# Add numbers and names to data
data["name"] = [name_number[0] for name_number in names_numbers]
data["number"] = [name_number[1] for name_number in names_numbers]

data.number = data.number.astype("Int64")  # Int64 supports integers and NaN
print(data.head())

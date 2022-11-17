#!/usr/bin/env python3

"""Instantiate the latest batch of ssoCards from a local store.

Call as

    python test_ssocards_local.py path/to/sscoard/store > ssocard_errors.txt
"""

import json
import os
import sys

import rocks
from tqdm import tqdm

if len(sys.argv) < 1:
    print("Script requires the path/to/ssocards/store as argument. Exiting.")
    sys.exit()

PATH_STORE = sys.argv[1]

# Retrieve gzipped ssoCard batch from SsODNet
print(f"Checking ssoCards in {PATH_STORE}..", file=sys.stderr)

# Instantiate ssoCards with rocks
with open(os.path.join(PATH_STORE, "ssocards.list"), "r") as file_:
    CARDS = [
        os.path.join(PATH_STORE, path.split("store/")[-1])
        for path in file_.read().split()
    ]

for card in tqdm(CARDS, total=len(CARDS), desc="Validating Cards"):

    with open(card, "r") as card_:
        ssoCard = json.load(card_)

    rocks.Rock(os.path.basename(card), ssocard=ssoCard, skip_id_check=True)

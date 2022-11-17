#!/usr/bin/env python3

"""Download and instantiate the latest batch of ssoCards.

Call as

    python test_ssocards.py > ssocard_errors.txt
"""

import glob
import json
import os
import shutil
import sys
import tarfile

import requests
import rocks
from tqdm import tqdm

URL = "https://ssp.imcce.fr/webservices/ssodnet/api/ssocard/ssoCard-latest.tar.bz2"
PATH_GZIP = "/tmp/ssoCard-latest.tar.bz2"
PATH_CARDS = "/tmp/ssocards/"

# Retrieve gzipped ssoCard batch from SsODNet
print(f"Retrieving ssoCards to {PATH_GZIP}..", file=sys.stderr)
with requests.get(URL, stream=True) as response:

    total = int(response.headers.get("content-length", 0))

    with open(PATH_GZIP, "wb") as file_, tqdm(
        total=total,
        unit="iB",
        unit_scale=True,
        unit_divisor=1024,
    ) as progress:

        for chunk in response.iter_content(chunk_size=1024):
            size = file_.write(chunk)
            progress.update(size)

# Unpack cards into /tmp
print(
    f"Unpacking ssoCards to {PATH_CARDS}.. [takes 5min to open archive]",
    file=sys.stderr,
)
with tarfile.open(PATH_GZIP, mode="r:bz2") as tar:
    for member in tqdm(iterable=tar.getmembers(), total=len(tar.getmembers())):
        tar.extract(member=member, path=PATH_CARDS)

# Restructure for easier file access
for dir in glob.glob(f"{PATH_CARDS}/*/store/*"):
    shutil.move(dir, PATH_CARDS)

# Instantiate ssoCards with rocks
with open(os.path.join(PATH_CARDS, "ssocards.list"), "r") as file_:
    CARDS = [
        os.path.join(PATH_CARDS, path.split("store/")[-1])
        for path in file_.read().split()
    ]

for card in tqdm(CARDS, total=len(CARDS), desc="Validating Cards"):

    with open(card, "r") as card_:
        ssoCard = json.load(card_)

    rocks.Rock(os.path.basename(card), ssocard=ssoCard, skip_id_check=True)

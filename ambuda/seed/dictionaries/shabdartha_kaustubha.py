#!/usr/bin/env python3
"""Add the śabdārthakaustubha dictionary to the database.

(Sanskrit-Kannada)
"""

import re

import click
from indic_transliteration import sanscript

from ambuda.seed.utils.cdsl_utils import create_from_scratch
from ambuda.seed.utils.data_utils import create_db, fetch_text
from ambuda.utils.dict_utils import standardize_key

RAW_URL = "https://raw.githubusercontent.com/indic-dict/stardict-sanskrit/raw/master/sa-head/other-indic-entries/shabdArtha_kaustubha/shabdArtha_kaustubha.babylon"


def _create_entries(key, body):
    if not re.match(r"^[a-zA-Z|]+$", key):
        print(f"  bad key: {key}")
        return

    body = re.sub(r"\[(.*)\]", r"<lb/><b>\1</b>", body)

    # Per vishvas, '|' divides headwords.
    for key in key.split("|"):
        key = standardize_key(key)
        yield key, f"<s>{body}</s>"


def sak_generator(dict_blob: str):
    buf = []
    for line in dict_blob.splitlines():
        if line.startswith("#"):
            continue

        line = line.strip()
        if line:
            line = sanscript.transliterate(line, sanscript.DEVANAGARI, sanscript.SLP1)
            # Standardize on CDSL conventions, mostly
            line = line.replace("<br>", "<lb/>")
            buf.append(line)
        elif buf:
            key, body = buf
            yield from _create_entries(key, body)
            buf = []
    if buf:
        key, body = buf
        yield from _create_entries(key, body)


@click.command()
@click.option("--use-cache/--no-use-cache", default=False)
def run(use_cache):
    print("Initializing database ...")
    engine = create_db()

    print(f"Fetching data from GitHub (use_cache = {use_cache})...")
    text_blob = fetch_text(RAW_URL, read_from_cache=use_cache)

    print("Adding items to database ...")
    create_from_scratch(
        engine,
        slug="shabdartha-kaustubha",
        title="Shabdarthakaustubha",
        generator=sak_generator(text_blob),
    )

    print("Done.")


if __name__ == "__main__":
    run()

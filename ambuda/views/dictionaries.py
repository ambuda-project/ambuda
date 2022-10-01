from flask import Blueprint, abort, redirect, render_template, url_for
from indic_transliteration import detect, sanscript

import ambuda.queries as q
from ambuda.utils import xml
from ambuda.utils.dict_utils import expand_apte_keys, expand_skd_keys, standardize_key
from ambuda.views.api import bp as api

bp = Blueprint("dictionaries", __name__)


def _fetch_entries(sources: list[str], query: str) -> list[str]:
    query = query.strip()
    input_scheme = detect.detect(query)

    slp1_key = sanscript.transliterate(query, input_scheme, sanscript.SLP1)
    slp1_key = standardize_key(slp1_key)

    keys = [slp1_key]
    if any(x in sources for x in {"apte", "apte-sh"}):
        keys.extend(expand_apte_keys(slp1_key))
    if "shabdakalpadruma" in sources:
        keys.extend(expand_skd_keys(slp1_key))

    rows = q.dict_entries(sources, keys)
    transforms = {
        "apte": xml.transform_apte_sanskrit_english,
        "apte-sh": xml.transform_apte_sanskrit_hindi,
        "shabdartha-kaustubha": xml.transform_sak,
        "mw": xml.transform_mw,
        "vacaspatyam": xml.transform_vacaspatyam,
        "shabdakalpadruma": xml.transform_mw,
    }
    fn = transforms.get(version, xml.transform_mw)
    return [fn(r.value) for r in rows]


@bp.route("/")
def index():
    """Show the dictionary lookup tool."""
    return render_template("dictionaries/index.html")


@bp.route("/<slug>/")
def version(slug):
    dictionaries = q.dictionaries()
    if slug not in dictionaries:
        abort(404)
    # TODO: set chosen dictionary as UX view
    return redirect(url_for("dictionaries.index"))


@bp.route("/<list:sources>/<query>")
def entry(sources, query):
    """Show a specific dictionary entry."""
    dictionaries = q.dictionaries()
    # if source not in dictionaries:
    #     abort(404)

    entries = _fetch_entries(sources, query)
    return render_template("dictionaries/index.html", query=query, entries=entries)


@api.route("/dictionaries/<list:sources>/<query>")
def entry_htmx(sources, query):
    dictionaries = q.dictionaries()
    # if source not in dictionaries:
    #    abort(404)

    entries = _fetch_entries(sources, query)
    return render_template("htmx/dictionary-results.html", query=query, entries=entries)

"""``tltk`` gives the IPA and tone digits of Piper's Thai phonemizer.

The expected values in ``data/piper_tltk.jsonl`` come from OHF-Voice/piper1-gpl
at d76f335d9eb5dea5ef6d7d70b2d6114e6303fa08, built from that checkout with
tltk 1.10 and unicode-rbnf 2.4.1. Each expected value is

    ThaiPhonemizer().phonemize(text)

with ``from piper.phonemize_thai import ThaiPhonemizer``. The rows include
digits, because the backend reads numbers itself. TLTK gives another reading
of some sentences after it has read others, in Piper too, so the sample holds
only sentences whose reading does not depend on the order.
"""
from importlib import metadata

import pytest

from scriptconv_copyleft.phonemizers.th import TLTKPhonemizer
from tests.piper_parity import parity_rows

ROWS = parity_rows("tltk")


@pytest.fixture(scope="module")
def phonemizer():
    return TLTKPhonemizer()


@pytest.mark.parametrize("text, expected", ROWS)
def test_matches_piper(phonemizer, text, expected):
    assert phonemizer.phonemize(text, "th") == expected


def test_the_rows_hold_numbers():
    assert any(any(c.isdigit() for c in text) for text, _ in ROWS)


def test_the_backend_owns_normalisation():
    assert TLTKPhonemizer.owned_stages == frozenset({"normalize"})


def test_identity_names_tltk():
    identity = TLTKPhonemizer().identity("th-TH")
    assert (identity.distribution, identity.version, identity.lang) == \
        ("tltk", metadata.version("tltk"), "th")

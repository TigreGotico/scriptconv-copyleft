"""``hebrew_ipa`` gives the IPA that Piper's Hebrew G2P gives for the same niqqud text.

The expected values in ``data/piper_hebrew_ipa.jsonl`` come from
OHF-Voice/piper1-gpl at d76f335d9eb5dea5ef6d7d70b2d6114e6303fa08, built from
that checkout. Each input is the niqqud text that Piper feeds its G2P (the
Nakdimon output for undotted text), and each expected value is

    HebrewPhonemizer().phonemize(text)

with ``from piper.phonemize_hebrew import HebrewPhonemizer``.
"""
from importlib import metadata

import pytest
from scriptconv.phonemizers.base import UnsupportedLanguageError

from scriptconv_copyleft.phonemizers.he import HebrewIPAPhonemizer
from tests.piper_parity import parity_rows

ROWS = parity_rows("hebrew_ipa")


@pytest.fixture(scope="module")
def phonemizer():
    return HebrewIPAPhonemizer()


@pytest.mark.parametrize("text, expected", ROWS)
def test_matches_piper(phonemizer, text, expected):
    assert phonemizer.phonemize(text, "he") == expected


@pytest.mark.parametrize("text, expected", ROWS[:5])
def test_the_string_is_the_one_sentence(phonemizer, text, expected):
    assert phonemizer.phonemize_string(text, "he") == "".join(expected[0])


def test_other_languages_are_refused(phonemizer):
    with pytest.raises(UnsupportedLanguageError):
        phonemizer.phonemize("שָׁלוֹם", "ar")


def test_identity_names_this_package():
    identity = HebrewIPAPhonemizer().identity("he-IL")
    assert (identity.distribution, identity.version, identity.lang) == \
        ("scriptconv-copyleft", metadata.version("scriptconv-copyleft"), "he")

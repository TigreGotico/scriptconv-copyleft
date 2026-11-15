"""``espeak_lt_accent`` gives the IPA and pitch accents of Piper's Lithuanian phonemizer.

The expected values in ``data/piper_espeak_lt_accent.jsonl`` come from
OHF-Voice/piper1-gpl at d76f335d9eb5dea5ef6d7d70b2d6114e6303fa08, built from
that checkout. Each expected value is

    LithuanianPhonemizer().phonemize(text)

with ``from piper.phonemize_lithuanian import LithuanianPhonemizer``. Piper
calls the espeak-ng library at commit 724808c; this backend calls the
espeak-ng 1.52.0 binary, and the rows are ones where both give the same
phonemes.
"""
from unittest import mock

import pytest

from scriptconv_copyleft.phonemizers.lt import EspeakLithuanianAccentPhonemizer
from tests.piper_parity import parity_rows

ROWS = parity_rows("espeak_lt_accent")


@pytest.fixture(scope="module")
def phonemizer():
    return EspeakLithuanianAccentPhonemizer()


@pytest.mark.parametrize("text, expected", ROWS)
def test_matches_piper(phonemizer, text, expected):
    assert phonemizer.phonemize(text, "lt") == expected


def test_the_wheel_ships_the_stress_dictionary(phonemizer):
    assert len(phonemizer.dictionary) == 189_262


def test_identity_reports_the_binary():
    banner = "eSpeak NG text-to-speech: 1.52.0  Data at: /usr/share/espeak-ng-data"
    with mock.patch.object(EspeakLithuanianAccentPhonemizer, "_has_binary", return_value=True), \
            mock.patch.object(EspeakLithuanianAccentPhonemizer, "_run_espeak_command", return_value=banner):
        identity = EspeakLithuanianAccentPhonemizer().identity("lt-LT")
    assert (identity.distribution, identity.version, identity.lang) == ("espeak-ng", "1.52.0", "lt")

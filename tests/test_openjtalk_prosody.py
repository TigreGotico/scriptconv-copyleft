"""``openjtalk_prosody`` gives the IPA and accent marks of Piper's Japanese phonemizer.

The expected values in ``data/piper_openjtalk_prosody.jsonl`` come from
OHF-Voice/piper1-gpl at d76f335d9eb5dea5ef6d7d70b2d6114e6303fa08, built from
that checkout with pyopenjtalk-plus 0.4.1.post10. Each expected value is

    JapanesePhonemizer().phonemize(text)

with ``from piper.phonemize_japanese import JapanesePhonemizer``. The readings
come from the OpenJTalk dictionary, so the test extra installs pyopenjtalk-plus,
the distribution that Piper uses. With pyopenjtalk 0.4.1, which the
``ja-phonemizers`` extra installs, 993 of 1033 parity sentences get other
readings, so most rows here fail.
"""
from importlib import metadata

import pytest

from scriptconv_copyleft.phonemizers.ja_prosody import OpenJTalkProsodyPhonemizer
from tests.piper_parity import parity_rows

ROWS = parity_rows("openjtalk_prosody")


@pytest.fixture(scope="module")
def phonemizer():
    return OpenJTalkProsodyPhonemizer()


@pytest.mark.parametrize("text, expected", ROWS)
def test_matches_piper(phonemizer, text, expected):
    assert phonemizer.phonemize(text, "ja") == expected


def test_the_string_joins_the_sentences(phonemizer):
    text, expected = next((t, e) for t, e in ROWS if len(e) > 1)
    assert phonemizer.phonemize_string(text, "ja") == " ".join("".join(s) for s in expected)


def test_identity_names_the_installed_openjtalk():
    distribution = metadata.packages_distributions()["pyopenjtalk"][0]
    identity = OpenJTalkProsodyPhonemizer().identity("ja-JP")
    assert distribution in ("pyopenjtalk", "pyopenjtalk-plus")
    assert (identity.distribution, identity.version, identity.lang) == \
        (distribution, metadata.version(distribution), "ja")

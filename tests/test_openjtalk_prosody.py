"""``openjtalk_prosody`` gives the IPA and accent marks of Piper's Japanese phonemizer.

The expected values in ``data/piper_openjtalk_prosody.jsonl`` come from
OHF-Voice/piper1-gpl at d76f335d9eb5dea5ef6d7d70b2d6114e6303fa08, built from
that checkout with pyopenjtalk-plus 0.4.1.post10. Each expected value is

    JapanesePhonemizer().phonemize(text)

with ``from piper.phonemize_japanese import JapanesePhonemizer``. The backend
runs only on pyopenjtalk-plus with onnxruntime, as Piper does. pyopenjtalk
0.4.1 gives other readings for 993 of 1033 parity sentences, and without
onnxruntime pyopenjtalk-plus reads 何時 as なにじ.
"""
import sys
from importlib import metadata

import pytest
from scriptconv.phonemizers import openjtalk_engine

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


def test_identity_names_pyopenjtalk_plus():
    identity = OpenJTalkProsodyPhonemizer().identity("ja-JP")
    assert (identity.distribution, identity.version, identity.lang) == \
        ("pyopenjtalk-plus", metadata.version("pyopenjtalk-plus"), "ja")


def test_refuses_the_pyopenjtalk_module(monkeypatch):
    # scriptconv's engine check reads which distribution owns the module.
    monkeypatch.setattr(openjtalk_engine, "module_distribution", lambda module, module_file: "pyopenjtalk")
    with pytest.raises(ImportError, match="comes from pyopenjtalk\\."):
        OpenJTalkProsodyPhonemizer()


def test_refuses_to_run_without_onnxruntime(monkeypatch):
    monkeypatch.setitem(sys.modules, "onnxruntime", None)
    with pytest.raises(ImportError, match="onnxruntime"):
        OpenJTalkProsodyPhonemizer()

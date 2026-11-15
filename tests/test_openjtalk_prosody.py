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
import base64
import hashlib
import sys
from importlib import metadata
from types import SimpleNamespace

import pyopenjtalk
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


def test_identity_names_pyopenjtalk_plus():
    identity = OpenJTalkProsodyPhonemizer().identity("ja-JP")
    assert (identity.distribution, identity.version, identity.lang) == \
        ("pyopenjtalk-plus", metadata.version("pyopenjtalk-plus"), "ja")


VERSIONS = {"pyopenjtalk": "0.4.1", "pyopenjtalk-plus": "0.4.1.post10"}


def _record_hash(content: bytes) -> SimpleNamespace:
    value = base64.urlsafe_b64encode(hashlib.sha256(content).digest()).rstrip(b"=").decode()
    return SimpleNamespace(mode="sha256", value=value)


@pytest.fixture
def both_installed(tmp_path, monkeypatch):
    """pyopenjtalk and pyopenjtalk-plus both record ``pyopenjtalk/__init__.py``.

    The file on disk holds the content of the distribution that the test names
    as the owner, as when that distribution was installed last.
    """
    module_file = tmp_path / "pyopenjtalk" / "__init__.py"
    module_file.parent.mkdir()
    contents = {name: f"# {name}\n".encode() for name in VERSIONS}

    def install(owner: str, order: list[str]):
        module_file.write_bytes(contents[owner])
        dists = {name: SimpleNamespace(files=[SimpleNamespace(hash=_record_hash(contents[name]),
                                                              locate=lambda: module_file)])
                 for name in VERSIONS}
        monkeypatch.setattr(pyopenjtalk, "__file__", str(module_file))
        monkeypatch.setattr(metadata, "packages_distributions", lambda: {"pyopenjtalk": order})
        monkeypatch.setattr(metadata, "distribution", dists.__getitem__)
        monkeypatch.setattr(metadata, "version", VERSIONS.__getitem__)

    return install


@pytest.mark.parametrize("order", [["pyopenjtalk", "pyopenjtalk-plus"], ["pyopenjtalk-plus", "pyopenjtalk"]])
def test_identity_names_the_distribution_that_owns_the_module(both_installed, order):
    both_installed("pyopenjtalk-plus", order)
    identity = OpenJTalkProsodyPhonemizer().identity("ja")
    assert (identity.distribution, identity.version) == ("pyopenjtalk-plus", "0.4.1.post10")


@pytest.mark.parametrize("order", [["pyopenjtalk", "pyopenjtalk-plus"], ["pyopenjtalk-plus", "pyopenjtalk"]])
def test_refuses_the_pyopenjtalk_module(both_installed, order):
    both_installed("pyopenjtalk", order)
    with pytest.raises(ImportError, match="comes from pyopenjtalk\\."):
        OpenJTalkProsodyPhonemizer()


def test_refuses_to_run_without_onnxruntime(monkeypatch):
    monkeypatch.setitem(sys.modules, "onnxruntime", None)
    with pytest.raises(ImportError, match="onnxruntime"):
        OpenJTalkProsodyPhonemizer()

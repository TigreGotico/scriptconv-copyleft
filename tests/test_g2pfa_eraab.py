"""The g2pfa wrapper passes the output format to the ``output_format``
parameter of persian_phonemizer.

A stand-in module replaces persian_phonemizer, which pulls torch through
g2p-fa. Its ``Phonemizer`` has the signature of the real class in
persian_phonemizer 0.4.0, ``persian_phonemizer/Phonemizer.py:20``:
``def __init__(self, preserve_punctuations=True, output_format="IPA"):``
"""
import sys
import types

import pytest
from scriptconv.phonemizers import Alphabet

from scriptconv_copyleft.phonemizers.fa import PersianPhonemizer


class _Phonemizer:
    def __init__(self, preserve_punctuations=True, output_format="IPA"):
        self.output_format = output_format

    def phonemize(self, text):
        return self.output_format


@pytest.fixture(autouse=True)
def _stand_in(monkeypatch):
    monkeypatch.setitem(sys.modules, "persian_phonemizer", types.SimpleNamespace(Phonemizer=_Phonemizer))


@pytest.mark.parametrize(("alphabet", "output_format"), [(Alphabet.ERAAB, "eraab"), (Alphabet.IPA, "IPA")])
def test_the_alphabet_reaches_output_format(alphabet, output_format):
    assert PersianPhonemizer(alphabet=alphabet).phonemize_string("سلام دنیا", "fa") == output_format

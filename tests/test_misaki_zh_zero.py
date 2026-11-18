"""misaki zh reads the zero sign 〇 (U+3007) as it reads 零.

Wiktionary, "〇", Chinese: "Used to express a zero digit in a number", with the sense of 零. The expected phonemes
are the ones misaki gives for the same text written with 零."""
import sys

import pytest

from scriptconv_copyleft.phonemizers.mul import MisakiPhonemizer, MisakiZhPhonemizer


@pytest.mark.skipif(sys.version_info >= (3, 13), reason="misaki declares Requires-Python <3.13")
@pytest.mark.parametrize("cls", [MisakiZhPhonemizer, MisakiPhonemizer])
@pytest.mark.parametrize("text", ["二〇二四", "〇 〇 七", "電話是五五五〇一〇〇。"])
def test_the_zero_sign_reads_as_zero(cls, text):
    phonemizer = cls()
    spoken = phonemizer.phonemize_string(text, "zh")
    assert "〇" not in spoken
    assert spoken == phonemizer.phonemize_string(text.replace("〇", "零"), "zh")

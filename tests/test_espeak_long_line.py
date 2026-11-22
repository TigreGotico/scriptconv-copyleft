"""espeak-ng reads a text longer than 999 bytes whole, to the last letter.

The text goes to espeak-ng on stdin. Without ``--stdin``, espeak-ng 1.52.0 reads
stdin with ``fgets`` into a 1,000-byte buffer (``src/espeak-ng.c``), so it cut a
longer line mid-word, and in UTF-8 text mid-character. With ``--stdin``, it
overwrites the last byte of the input, so the text needs a final newline.

The reference is espeak-ng's reading of the same text as one command-line
argument, which it synthesises in one call, and the reading of one sentence
alone, once per copy.
"""
import subprocess

import pytest

from scriptconv_copyleft.phonemizers.mul import EspeakPhonemizer

AR_SENTENCE = "ذهب الولد إلى المدرسة صباحا وقرأ كتابا جديدا عن تاريخ المدينة القديمة."
EN_SENTENCE = "The quick brown fox jumps over the lazy dog near the riverbank."


def argv_reading(text: str, voice: str) -> str:
    return subprocess.run(["espeak-ng", "-q", "-x", "--ipa", "-v", voice, "--", text],
                          capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()


@pytest.mark.parametrize("sentence, lang, voice", [(AR_SENTENCE, "ar", "ar"), (EN_SENTENCE, "en-US", "en-us")],
                         ids=["ar", "en"])
def test_a_line_longer_than_999_bytes_reads_every_word(sentence, lang, voice):
    copies = 2500 // len(sentence.encode("utf-8")) + 1
    text = " ".join([sentence] * copies)
    assert len(text.encode("utf-8")) > 2500
    phonemes = EspeakPhonemizer().phonemize_string(text, lang)
    assert phonemes == argv_reading(text, voice)
    assert phonemes.split() == argv_reading(sentence, voice).split() * copies


@pytest.mark.parametrize("text, lang, voice", [
    ("expected", "en-US", "en-us"),
    ("I expected it", "en-US", "en-us"),
    ("a", "en-US", "en-us"),
    ("مرحبا", "ar", "ar"),
    ("ع", "ar", "ar"),
])
def test_the_last_word_reads_whole(text, lang, voice):
    assert EspeakPhonemizer().phonemize_string(text, lang) == argv_reading(text, voice)

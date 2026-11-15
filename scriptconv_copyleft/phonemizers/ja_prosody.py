"""Japanese IPA with pitch accent marks, from OpenJTalk full-context labels.

Ported from Piper's Japanese phonemizer:
https://github.com/OHF-Voice/piper1-gpl/blob/d76f335d9eb5dea5ef6d7d70b2d6114e6303fa08/src/piper/phonemize_japanese.py
That file is GPL-3.0-or-later, the licence of piper1-gpl, so this module is
GPL-3.0-or-later too.

OpenJTalk reads the kanji, and its labels carry the accent of each accent
phrase. The labels are read into the accent-annotated form of ESPnet's
``pyopenjtalk_prosody`` G2P, and each OpenJTalk phone is then mapped to IPA.
The prosody symbols:

- ``↑`` accent rise (low to high, inside an accent phrase)
- ``↓`` accent fall (the accent nucleus)
- ``#`` accent phrase boundary
- ``,`` pause (OpenJTalk ``pau``, for example from 、)
- ``.`` end of a declarative sentence
- ``?`` end of an interrogative sentence
"""

import logging
import re
from collections.abc import Iterator
from importlib import metadata

from scriptconv.phonemizers.base import BasePhonemizer, _check_alphabet
from scriptconv.phonemizers.enums import Alphabet

LOG = logging.getLogger(__name__)

ACCENT_RISE = "↑"
ACCENT_FALL = "↓"
ACCENT_PHRASE_BOUNDARY = "#"
PAUSE = ","
DECLARATIVE_END = "."
INTERROGATIVE_END = "?"

PROSODY_SYMBOLS = frozenset({ACCENT_RISE, ACCENT_FALL, ACCENT_PHRASE_BOUNDARY,
                             PAUSE, DECLARATIVE_END, INTERROGATIVE_END})

# Palatalized consonants all take ʲ (ny -> nʲ, not ɲ), so the series stays
# consistent. A long vowel stays two vowels, because it counts as two morae.
OPENJTALK_TO_IPA: dict[str, str] = {
    # vowels
    "a": "a",
    "i": "i",
    "u": "ɯ",
    "e": "e",
    "o": "o",
    # consonants
    "k": "k",
    "ky": "kʲ",
    "kw": "kʷ",
    "g": "ɡ",
    "gy": "ɡʲ",
    "gw": "ɡʷ",
    "s": "s",
    "sh": "ɕ",
    "z": "z",
    "j": "dʑ",
    "t": "t",
    "ts": "ts",
    "ty": "tʲ",
    "ch": "tɕ",
    "d": "d",
    "dy": "dʲ",
    "n": "n",
    "ny": "nʲ",
    "h": "h",
    "hy": "hʲ",
    "f": "ɸ",
    "b": "b",
    "by": "bʲ",
    "p": "p",
    "py": "pʲ",
    "m": "m",
    "my": "mʲ",
    "y": "j",
    "r": "ɾ",
    "ry": "ɾʲ",
    "w": "w",
    "v": "v",
    # moraic nasal ん and geminate closure っ
    "N": "ɴ",
    "cl": "ʔ",
}

# OpenJTalk writes a devoiced vowel in upper case (desU for です).
DEVOICED_VOWELS = frozenset("AIUEO")

# The phones that can end a mora and so carry an accent phrase boundary.
_MORA_FINAL_PHONES = frozenset({"a", "i", "u", "e", "o", "A", "I", "U", "E", "O", "N", "cl"})

# Sentence-final punctuation, with any closing brackets, quotes and spaces
# after it. OpenJTalk reads these as a pause only, so the text is split first.
_SENTENCE_END = re.compile(r"[。．！？!?]+[」』）】〉》”’\"')\]\s]*")

_CURRENT_PHONE = re.compile(r"\-(.*?)\+")

# The value of a label field that is unset ("xx") or absent, as in ESPnet.
_NO_FEATURE = -50


def _numeric_feature(pattern: str, label: str) -> int:
    match = re.search(pattern, label)
    if match is None:
        return _NO_FEATURE
    try:
        return int(match.group(1))
    except ValueError:
        return _NO_FEATURE


def _is_decimal_point(text: str, match: "re.Match[str]") -> bool:
    """True for the "." in "1.5", which does not end a sentence."""
    if match.group(0) != ".":
        return False
    before = text[match.start() - 1] if match.start() > 0 else ""
    after = text[match.end()] if match.end() < len(text) else ""
    return before.isdigit() and after.isdigit()


def split_sentences(text: str) -> list[str]:
    """The sentences of *text*, each with its final punctuation."""
    sentences: list[str] = []
    start = 0
    for match in _SENTENCE_END.finditer(text):
        if _is_decimal_point(text, match):
            continue
        sentence = text[start:match.end()].strip()
        if sentence:
            sentences.append(sentence)
        start = match.end()
    tail = text[start:].strip()
    if tail:
        sentences.append(tail)
    return sentences


class OpenJTalkProsodyPhonemizer(BasePhonemizer):
    """OpenJTalk readings in IPA, with accent rise, fall and phrase marks.

    Each symbol is one code point. Pauses and sentence ends are symbols too,
    so the backend reads the punctuation itself and splits its own sentences.

    Two distributions install the ``pyopenjtalk`` module: pyopenjtalk and
    pyopenjtalk-plus. Their dictionaries and accent rules differ, so the
    readings differ too. Piper uses pyopenjtalk-plus, and
    :meth:`identity` names the distribution that is installed.
    """

    def __init__(self, alphabet: Alphabet = Alphabet.IPA, drop_devoiced_vowels: bool = True):
        """
        Args:
            drop_devoiced_vowels: Write a devoiced vowel (A I U E O) as its
                voiced vowel. The context predicts most devoicing.
        """
        _check_alphabet(self, alphabet, [Alphabet.IPA])
        try:
            import pyopenjtalk
        except ImportError as e:
            raise ImportError(
                "pyopenjtalk is required for the OpenJTalk prosody phonemizer. "
                "Install it with 'pip install scriptconv[ja-phonemizers]'."
            ) from e
        self.pyopenjtalk = pyopenjtalk
        self.drop_devoiced_vowels = drop_devoiced_vowels
        super().__init__(alphabet)

    @classmethod
    def get_lang(cls, target_lang: str) -> str:
        return cls.match_lang(target_lang, ["ja"])

    def _engine_release(self) -> tuple[str, str]:
        distribution = metadata.packages_distributions()["pyopenjtalk"][0]
        return distribution, metadata.version(distribution)

    def openjtalk_phones(self, sentence: str) -> list[str]:
        """OpenJTalk phones and prosody symbols of one sentence, before the IPA mapping."""
        try:
            labels = self.pyopenjtalk.make_label(self.pyopenjtalk.run_frontend(sentence))
        except Exception:
            LOG.exception("OpenJTalk could not read the sentence: %s", sentence)
            return []

        phones: list[str] = []
        for index, label in enumerate(labels):
            match = _CURRENT_PHONE.search(label)
            if match is None:
                continue
            phone = match.group(1)
            if self.drop_devoiced_vowels and phone in DEVOICED_VOWELS:
                phone = phone.lower()

            if phone == "sil":
                # The first sil needs no symbol. The last one carries the
                # intonation: e3 == 1 in E:<e1>_<e2>!<e3>_ marks a question.
                if index == len(labels) - 1:
                    question = _numeric_feature(r"!(\d+)_", label) == 1
                    phones.append(INTERROGATIVE_END if question else DECLARATIVE_END)
                continue
            if phone == "pau":
                phones.append(PAUSE)
                continue

            phones.append(phone)
            if index >= len(labels) - 1:
                continue

            # a1: mora position relative to the accent nucleus (0 is the
            # nucleus); a2, a3: mora position from the start and from the end
            # of the accent phrase; f1: morae in the accent phrase.
            a1 = _numeric_feature(r"/A:([0-9\-]+)\+", label)
            a2 = _numeric_feature(r"\+(\d+)\+", label)
            a3 = _numeric_feature(r"\+(\d+)/", label)
            f1 = _numeric_feature(r"/F:(\d+)_", label)
            a2_next = _numeric_feature(r"\+(\d+)\+", labels[index + 1])

            if a3 == 1 and a2_next == 1 and phone in _MORA_FINAL_PHONES:
                phones.append(ACCENT_PHRASE_BOUNDARY)
            elif a1 == 0 and a2_next == a2 + 1 and a2 != f1:
                phones.append(ACCENT_FALL)
            elif a2 == 1 and a2_next == 2:
                phones.append(ACCENT_RISE)
        return phones

    def _sentence_ipa(self, sentence: str) -> list[str]:
        ipa: list[str] = []
        for phone in self.openjtalk_phones(sentence):
            if phone in PROSODY_SYMBOLS:
                ipa.append(phone)
            elif phone in OPENJTALK_TO_IPA:
                # kʲ, tɕ, dʑ and the other two-symbol phones become two symbols
                ipa.extend(OPENJTALK_TO_IPA[phone])
            else:
                LOG.warning("No IPA for the OpenJTalk phone: %s", phone)
        return ipa

    def _sentences(self, text: str, lang: str) -> Iterator[list[str]]:
        self.get_lang(lang)
        for sentence in split_sentences(text):
            ipa = self._sentence_ipa(sentence)
            if ipa:
                yield ipa

    def phonemize_lazy(self, text: str, lang: str) -> Iterator[list[str]]:
        if self.normalizer is not None:
            text = self.normalizer(text, lang)
        yield from self._sentences(text, lang)

    def phonemize_string(self, text: str, lang: str) -> str:
        return " ".join("".join(sentence) for sentence in self._sentences(text, lang))

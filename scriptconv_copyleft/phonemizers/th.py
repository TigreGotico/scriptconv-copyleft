"""Thai IPA with a tone digit after each syllable, from TLTK.

Ported from Piper's Thai phonemizer:
https://github.com/OHF-Voice/piper1-gpl/blob/d76f335d9eb5dea5ef6d7d70b2d6114e6303fa08/src/piper/phonemize_thai.py
That file is GPL-3.0-or-later, the licence of piper1-gpl, so this module is
GPL-3.0-or-later too. TLTK (BSD-3-Clause) segments the words, which Thai
writes without spaces, and gives syllabified IPA with one tone per syllable.

The tone digits: 1 mid, 2 low, 3 falling, 4 high, 5 rising. A space separates
two words, and the punctuation marks ``. , ? ! : ; -`` stay as symbols.

The backend reads numbers itself: Thai digits become Arabic digits, and
unicode-rbnf writes each number as Thai words, with ``฿`` read as บาท and
``%`` as เปอร์เซ็นต์. TLTK does not read digits.
"""

import logging
import re
import unicodedata
from collections.abc import Iterator

from scriptconv.phonemizers.base import BasePhonemizer, _check_alphabet
from scriptconv.phonemizers.enums import Alphabet

LOG = logging.getLogger(__name__)

TONES = frozenset("12345")

# The symbols a syllable may hold: the single code points of Piper's default
# phoneme id map (piper/phoneme_ids.py, DEFAULT_PHONEME_ID_MAP). A syllable
# with any other symbol is a word TLTK echoed back without a transcription.
SYMBOLS = frozenset(
    "_^$ !'(),-.:;?abcdefhijklmnopqrstuvwxyzæçðøħŋœǀǁǂǃɐɑɒɓɔɕɖɗɘəɚɛɜɞɟɠɡɢɣɤɥɦɧɨɪɫɬ"
    "ɭɮɯɰɱɲɳɴɵɶɸɹɺɻɽɾʀʁʂʃʄʈʉʊʋʌʍʎʏʐʑʒʔʕʘʙʛʜʝʟʡʢʲˈˌːˑ˞βθχᵻⱱ0123456789"
    "̧̪̯̩̃ʰˤε↓#\"↑̺̻gʦX̝̊ɝʷ")

# TLTK writes the open o as U+1D10 LATIN LETTER SMALL CAPITAL OPEN O, which
# means U+0254 LATIN SMALL LETTER OPEN O.
_TLTK_TO_IPA = {"ᴐ": "ɔ"}

# TLTK ends each chunk it transcribed with this marker.
_CHUNK_MARKER = "<s/>"

# A run of Thai that TLTK reads: consonants, vowels, tone marks and ๆ, which
# TLTK repeats itself. ฯ and the other marks in _SILENT are not in it, because
# TLTK reads them out by name.
_THAI_RUN = re.compile(r"[ก-ฮะ-ฺเ-๎]+")

# ฯลฯ ("et cetera") is read ละ. It is replaced before ฯ is removed.
_ET_CETERA = ("ฯลฯ", "ละ")

# Marks that are not spoken, and the zero-width characters that unicode-rbnf
# puts between number words. TLTK gives an empty transcription for a whole run
# that holds one of them.
_SILENT = re.compile("[ฯ๏๚๛\u200b\u200c\u200d\ufeff]")

# Letters that modern spelling replaced, and that TLTK's dictionary lacks.
_OBSOLETE = str.maketrans({"ฃ": "ข", "ฅ": "ค"})

_THAI_DIGITS = str.maketrans("๐๑๒๓๔๕๖๗๘๙", "0123456789")

# สระอำ (U+0E33) typed as nikhahit and sara aa, with a tone mark between them
# or not. NFC does not join them, and TLTK gives an empty transcription.
_SARA_AM = re.compile("ํ([่-๋]?)า")

# A thousands separator, so that 1,250 is one number.
_GROUPED_NUMBER = re.compile(r"(?<=\d),(?=\d{3}\b)")
# A minus counts only at a word boundary, so โควิด-19 keeps its hyphen.
_NUMBER = re.compile(r"(?<!\w)-?\d+(?:\.\d+)?")
_BAHT = re.compile(r"฿\s*(-?[\d.]+)")
_PERCENT = re.compile(r"(-?[\d.]+)\s*%")

_PUNCTUATION = frozenset(".,?!:;-")

# Thai has no sentence-final period, and a space is a clause break, so only
# explicit sentence-final punctuation and line breaks split sentences.
_SENTENCE_SPLIT = re.compile(r"(?<=[.?!])\s+|\n+")

_WORD_BREAK = " "


def _punctuation_phonemes(text: str) -> list[str]:
    """The text between two Thai runs as punctuation symbols and word breaks.

    Latin letters, digits that are left and other symbols become one word
    break each run.
    """
    phonemes: list[str] = []
    for char in text:
        if char in _PUNCTUATION:
            phonemes.append(char)
            continue
        if char.isalnum():
            LOG.warning("Dropping a character that is not Thai: %r", char)
        if not phonemes or phonemes[-1] != _WORD_BREAK:
            phonemes.append(_WORD_BREAK)
    return phonemes


class TLTKPhonemizer(BasePhonemizer):
    """Thai IPA from TLTK, with a tone digit after each syllable."""

    engine_distribution = "tltk"
    owned_stages = frozenset({"normalize"})

    def __init__(self, alphabet: Alphabet = Alphabet.IPA):
        _check_alphabet(self, alphabet, [Alphabet.IPA])
        try:
            from tltk.nlp import th2ipa
            from unicode_rbnf import RbnfEngine
        except ImportError as e:
            raise ImportError(
                "tltk and unicode-rbnf are required for the TLTK phonemizer. "
                "Install them with 'pip install scriptconv[th]'."
            ) from e
        self._th2ipa = th2ipa
        self.number_engine = RbnfEngine.for_language("th")
        super().__init__(alphabet)

    @classmethod
    def get_lang(cls, target_lang: str) -> str:
        return cls.match_lang(target_lang, ["th"])

    def _th_number(self, match: "re.Match[str]") -> str:
        try:
            return self.number_engine.format_number(match.group(0)).text
        except Exception:
            LOG.warning("Could not write the number as words: %s", match.group(0))
            return ""

    def _normalize(self, text: str) -> str:
        # Thai combining marks compose only in canonical order.
        text = unicodedata.normalize("NFC", text)
        text = text.translate(_THAI_DIGITS).translate(_OBSOLETE)
        text = _SARA_AM.sub("\\1ำ", text)
        text = text.replace(*_ET_CETERA)
        text = _GROUPED_NUMBER.sub("", text)
        text = _BAHT.sub(lambda m: f"{m.group(1)} บาท", text)
        text = _PERCENT.sub(lambda m: f"{m.group(1)} เปอร์เซ็นต์", text)
        # unicode-rbnf joins number words with zero-width spaces. Real spaces
        # make each word a run of its own, because TLTK drops the end of some
        # compounds that it splits itself (สิบเก้า gives only si2).
        text = _NUMBER.sub(self._th_number, text).replace("\u200b", " ")
        return _SILENT.sub("", text)

    def _syllable_phonemes(self, syllable: str, run: str) -> list[str]:
        # A silent letter (การันต์) leaves an empty syllable: พิมพ์ gives "pʰim1..".
        if not syllable:
            return []
        tone: str | None = None
        if syllable[-1] in TONES:
            syllable, tone = syllable[:-1], syllable[-1]
        phonemes: list[str] = []
        for char in syllable:
            char = _TLTK_TO_IPA.get(char, char)
            if char not in SYMBOLS:
                LOG.warning("Dropping the symbol %r that TLTK did not transcribe in: %s", char, run)
                return []
            phonemes.append(char)
        if phonemes and tone is not None:
            phonemes.append(tone)
        return phonemes

    def _run_phonemes(self, run: str) -> list[str]:
        """Segment and transcribe one run of Thai letters.

        TLTK takes one run at a time: a space, a Latin letter or punctuation in
        its input raises ``ValueError``. TLTK still segments the words inside
        the run.
        """
        try:
            transcription = self._th2ipa(run)
        except Exception:
            LOG.warning("TLTK could not transcribe the Thai run: %s", run)
            return []
        phonemes: list[str] = []
        # A space or <s/> separates two words, "." two syllables, and "+" the
        # parts of a spelled-out symbol.
        for word in transcription.replace(_CHUNK_MARKER, " ").split():
            word_phonemes: list[str] = []
            for syllable in re.split(r"[.+]", word):
                word_phonemes.extend(self._syllable_phonemes(syllable, run))
            if word_phonemes:
                if phonemes:
                    phonemes.append(_WORD_BREAK)
                phonemes.extend(word_phonemes)
        if not phonemes:
            LOG.warning("No phonemes for the Thai run: %s", run)
        return phonemes

    def _sentence_phonemes(self, sentence: str) -> list[str]:
        sentence = self._normalize(sentence)
        phonemes: list[str] = []
        position = 0
        for match in _THAI_RUN.finditer(sentence):
            phonemes.extend(_punctuation_phonemes(sentence[position:match.start()]))
            phonemes.extend(self._run_phonemes(match.group()))
            position = match.end()
        phonemes.extend(_punctuation_phonemes(sentence[position:]))
        while phonemes and phonemes[0] == _WORD_BREAK:
            phonemes.pop(0)
        while phonemes and phonemes[-1] == _WORD_BREAK:
            phonemes.pop()
        return phonemes

    def _sentences(self, text: str, lang: str) -> Iterator[list[str]]:
        self.get_lang(lang)
        for sentence in _SENTENCE_SPLIT.split(text):
            phonemes = self._sentence_phonemes(sentence)
            if phonemes:
                yield phonemes

    def phonemize_lazy(self, text: str, lang: str) -> Iterator[list[str]]:
        if self.normalizer is not None:
            text = self.normalizer(text, lang)
        yield from self._sentences(text, lang)

    def phonemize_string(self, text: str, lang: str) -> str:
        return " ".join("".join(sentence) for sentence in self._sentences(text, lang))

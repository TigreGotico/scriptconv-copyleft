"""Lithuanian IPA from espeak-ng, with the pitch accent from a stress dictionary.

Ported from Piper's Lithuanian phonemizer:
https://github.com/OHF-Voice/piper1-gpl/blob/d76f335d9eb5dea5ef6d7d70b2d6114e6303fa08/src/piper/phonemize_lithuanian.py
That file is GPL-3.0-or-later, the licence of piper1-gpl, so this module is
GPL-3.0-or-later too.

espeak-ng gives the phonemes of each word, one word at a time. Then:

1. ʂ, which espeak-ng writes for a plain "s" in some contexts (visi), becomes
   s. ɭ stays: it is espeak-ng's soft l, against the syllabic l̩ of the hard l.
2. The word is looked up in the stress dictionary (word, vowel group, accent).
3. The stress mark moves to the syllable that carries the accent, as one of
   three marks: ˈ for the acute (tvirtapradė), ˌ for the circumflex
   (tvirtagalė) and ˋ (U+02CB) for the short accent (trumpinė).

A word that is not in the dictionary keeps the stress of espeak-ng. The
dictionary holds one entry for each spelling, so two words that differ only
in accent (nãmo, namõ) get the same accent.

The data in ``_vendored/piper_lt`` comes from the same Piper commit.
``lt_kirciai.tsv`` (the stress dictionary) is CC-BY-4.0, built from the LIEPA
corpus annotation (Vilnius University, huggingface.co/datasets/meldynamics/liepa-tts)
and the g2p-lt-lexicon of Arunas Smaliukas (github.com/svogunas/g2p-lt-lexicon).
``lt_raides.tsv`` (letter names) and ``lt_kreipiniai.tsv`` (nouns of direct
address) are GPL-3.0-or-later. ``LICENSE`` and ``SOURCE`` in that directory
give the attribution.
"""

import re
import unicodedata
from collections.abc import Iterator
from pathlib import Path

from scriptconv_copyleft.phonemizers.mul import EspeakPhonemizer

ESPEAK_VOICE = "lt"

DATA_DIR = Path(__file__).parent / "_vendored" / "piper_lt"
DEFAULT_DICTIONARY_PATH = DATA_DIR / "lt_kirciai.tsv"
DEFAULT_LETTERS_PATH = DATA_DIR / "lt_raides.tsv"
DEFAULT_VOCATIVES_PATH = DATA_DIR / "lt_kreipiniai.tsv"

ACUTE = "ˈ"  # tvirtapradė, U+02C8, the primary stress of espeak-ng
CIRCUMFLEX = "ˌ"  # tvirtagalė, U+02CC, the secondary stress of espeak-ng
GRAVE = "ˋ"  # trumpinė, U+02CB
STRESS_MARKS = ACUTE + CIRCUMFLEX + GRAVE

IPA_VOWELS = "aeiouɑɐɔɛɪʊæøɘəɜ"
LENGTH = "ː"
# Symbols that belong to the consonant before them.
CONSONANT_MODIFIERS = "ʲʷʰ̩"

_LT_LETTERS = "a-zA-ZąčęėįšųūžĄČĘĖĮŠŲŪŽ"
_WORD_CLEAN = re.compile(f"[^{_LT_LETTERS}0-9]")

# Each word is read alone, so espeak-ng never sees the punctuation. The
# punctuation of a word follows its phonemes; other marks are dropped.
_KEEP_PUNCT = ".,!?:;"

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?…])\s+")

# The language switch marks of espeak-ng, "(en)" and "(lt)".
_LANG_FLAGS = re.compile(r"\([^)]+\)")

# The espeak-ng reading of each distinct word is kept for the life of the
# phonemizer, up to this many words. Then the cache is emptied.
CACHE_LIMIT = 250_000

# letter -> (IPA, word prefixes after which it is an abbreviation)
Letters = dict[str, tuple[str, tuple[str, ...]]]

# Matching ignores the Lithuanian diacritics, so "teti" matches "tėti".
_STRIP_DIACRITICS = str.maketrans("ąčęėįšųūžĄČĘĖĮŠŲŪŽ", "aceeisuuzACEEISUUZ")
_VOCATIVE_OPENERS = (",", ":", "-", "–", "—")
_VOCATIVE_CLOSERS = (",", ".", "!", "?", "…")


def load_letters(path: str | Path) -> Letters:
    """letter<TAB>IPA[<TAB>prefix,prefix] -> {letter: (IPA, prefixes)}.

    The names of the letters that espeak-ng reads wrong ("el" becomes
    "elektroninis"), and the words after which the same token is an
    abbreviation ("el. paštas"). A line that starts with # is a comment.
    """
    letters: Letters = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 2 or not parts[1]:
                continue
            prefixes = tuple(p for p in parts[2].split(",") if p) if len(parts) > 2 else ()
            letters[parts[0].lower()] = (parts[1], prefixes)
    return letters


def letter_ipa(word: str, next_word: str, letters: Letters) -> str | None:
    """The IPA of a letter name, or None when the token is an abbreviation."""
    entry = letters.get(word.lower())
    if entry is None:
        return None
    ipa, prefixes = entry
    for prefix in prefixes:
        if next_word.lower().startswith(prefix):
            return None
    return ipa


def load_vocatives(path: str | Path) -> frozenset:
    """word[<TAB>note] -> {word}, without diacritics.

    The nouns that occur as direct address. An empty file turns the vocative
    rule off.
    """
    words = set()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                continue
            word = line.rstrip("\n").split("\t")[0].strip().lower()
            if word:
                words.add(word.translate(_STRIP_DIACRITICS))
    return frozenset(words)


def is_vocative(words: list[str], tokens: list[str], i: int, vocatives: frozenset) -> bool:
    """True when word *i* is a listed noun with a comma or a sentence edge on each side.

    "Labas, mama." is an address; "Mano mama grįžo." is not.
    """
    if not vocatives:
        return False
    if words[i].lower().translate(_STRIP_DIACRITICS) not in vocatives:
        return False
    opened = i == 0 or tokens[i - 1].rstrip().endswith(_VOCATIVE_OPENERS)
    closed = i == len(tokens) - 1 or tokens[i].rstrip().endswith(_VOCATIVE_CLOSERS)
    return opened and closed


def ipa_vowel_groups(ipa: str) -> list[int]:
    """The start index of each vowel group (adjacent vowels and ː are one group)."""
    groups, i = [], 0
    while i < len(ipa):
        if ipa[i] in IPA_VOWELS:
            start = i
            while i + 1 < len(ipa) and (ipa[i + 1] in IPA_VOWELS or ipa[i + 1] == LENGTH):
                i += 1
            groups.append(start)
        i += 1
    return groups


def place_accent(ipa: str, group_index: int | None, mark: str) -> str:
    """Remove the stress of espeak-ng and put *mark* before the syllable of vowel group *group_index*.

    The syllable boundary follows Lithuanian phonotactics: V-CV, VC-CV, and a
    word-initial consonant cluster belongs to the first syllable.
    """
    clean = "".join(c for c in ipa if c not in STRESS_MARKS)
    groups = ipa_vowel_groups(clean)
    if group_index is None or group_index >= len(groups):
        return ipa
    p = groups[group_index]
    i = p - 1
    while i >= 0 and clean[i] in CONSONANT_MODIFIERS:
        i -= 1
    if i >= 0 and clean[i] not in IPA_VOWELS and clean[i] not in " " + LENGTH:
        i -= 1  # one consonant
    boundary = i + 1
    j = i
    while j >= 0 and clean[j] not in IPA_VOWELS and clean[j] != " ":
        j -= 1
    if j < 0 or clean[j] == " ":  # word start
        boundary = j + 1
    return clean[:boundary] + mark + clean[boundary:]


def vocative_accent(ipa: str) -> str:
    """Accent the first syllable and lengthen its vowel: mama -> ˈmaːːma.

    Only a first vowel group that is one short vowel becomes longer. A
    diphthong or a long vowel keeps its length.
    """
    accented = place_accent(ipa, 0, ACUTE)
    groups = ipa_vowel_groups(accented)
    if not groups:
        return accented
    start = groups[0]
    end = start
    while end + 1 < len(accented) and (accented[end + 1] in IPA_VOWELS or accented[end + 1] == LENGTH):
        end += 1
    if end != start:
        return accented
    return accented[:end + 1] + LENGTH * 2 + accented[end + 1:]


def load_dictionary(path: str | Path) -> dict[str, tuple[int, str]]:
    """word<TAB>vowel group index<TAB>mark[<TAB>IPA group index] -> {word: (group index, mark)}.

    The second column counts the vowel groups of the letters. espeak-ng
    splits some diphthongs into three sounds ("vaikai" gives vaːjɪkai), and
    for those words the optional fourth column gives the vowel group of the
    IPA, which is the index returned. A line that starts with # or that does
    not fit is skipped.
    """
    entries: dict[str, tuple[int, str]] = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) not in (3, 4) or parts[2] not in STRESS_MARKS:
                continue
            group = parts[3] if len(parts) == 4 else parts[1]
            entries[parts[0]] = (int(group), parts[2])
    return entries


class EspeakLithuanianAccentPhonemizer(EspeakPhonemizer):
    """Lithuanian espeak-ng IPA with the three pitch accents of the stress dictionary.

    The punctuation ``. , ! ? : ;`` of a word follows its phonemes, so the
    backend reads the punctuation itself and splits its own sentences.
    """

    def __init__(self, prefer_espyak: bool = False,
                 dictionary_path: str | Path = DEFAULT_DICTIONARY_PATH,
                 letters_path: str | Path = DEFAULT_LETTERS_PATH,
                 vocatives_path: str | Path = DEFAULT_VOCATIVES_PATH):
        """
        Args:
            prefer_espyak: Use the espyak port of espeak-ng even when the
                espeak-ng binary is installed.
            dictionary_path: The stress dictionary. The default is the one
                this package ships.
            letters_path: The letter names, see :func:`load_letters`.
            vocatives_path: The nouns of direct address, see
                :func:`load_vocatives`. An empty file turns the rule off.
        """
        super().__init__(prefer_espyak)
        self.dictionary = load_dictionary(dictionary_path)
        self.letters = load_letters(letters_path)
        self.vocatives = load_vocatives(vocatives_path)
        self._cache: dict[str, str] = {}
        self.cache_limit = CACHE_LIMIT

    @classmethod
    def get_lang(cls, target_lang: str) -> str:
        return cls.match_lang(target_lang, [ESPEAK_VOICE])

    def _espeak_word(self, word: str) -> str:
        ipa = self._cache.get(word)
        if ipa is None:
            if len(self._cache) >= self.cache_limit:
                self._cache.clear()
            ipa = super().phonemize_string(word, ESPEAK_VOICE)
            ipa = unicodedata.normalize("NFD", _LANG_FLAGS.sub("", ipa)).strip()
            # espeak-ng writes ʂ for some s (Fisichella, Estrellas). Lithuanian
            # has no ʂ, and Piper writes it as s.
            ipa = ipa.replace("ʂ", "s")
            self._cache[word] = ipa
        return ipa

    def phonemize_word(self, word: str) -> str:
        """One word (letters only) as IPA with its pitch accent."""
        ipa = self._espeak_word(word)
        entry = self.dictionary.get(word.lower())
        if entry is None:
            # espeak-ng's stress stays. A monosyllable without a mark takes
            # one before its vowel.
            if not any(c in STRESS_MARKS for c in ipa):
                groups = ipa_vowel_groups(ipa)
                if groups:
                    p = groups[0]
                    ipa = ipa[:p] + ACUTE + ipa[p:]
            return ipa
        group_index, mark = entry
        return place_accent(ipa, group_index, mark)

    def phonemize_sentence(self, sentence: str) -> str:
        pieces: list[str] = []
        tokens = sentence.split()
        words = [_WORD_CLEAN.sub("", t) for t in tokens]
        for i, token in enumerate(tokens):
            word = words[i]
            punct = "".join(c for c in token if c in _KEEP_PUNCT)
            if not word:
                if punct and pieces:
                    pieces[-1] += punct
                continue
            override = letter_ipa(word, words[i + 1] if i + 1 < len(words) else "", self.letters)
            ipa = override or self.phonemize_word(word)
            if override is None and is_vocative(words, tokens, i, self.vocatives):
                ipa = vocative_accent(ipa)
            pieces.append(ipa + punct)
        return " ".join(pieces)

    def _sentences(self, text: str, lang: str) -> Iterator[list[str]]:
        self.get_lang(lang)
        for sentence in _SENTENCE_SPLIT.split(text.strip()):
            if not sentence:
                continue
            ipa = self.phonemize_sentence(sentence)
            if ipa:
                yield list(unicodedata.normalize("NFD", ipa))

    def phonemize_lazy(self, text: str, lang: str) -> Iterator[list[str]]:
        if self.normalizer is not None:
            text = self.normalizer(text, lang)
        yield from self._sentences(text, lang)

    def phonemize_string(self, text: str, lang: str) -> str:
        return " ".join("".join(sentence) for sentence in self._sentences(text, lang))

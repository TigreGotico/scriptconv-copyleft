"""Dictionary-backed Japanese respelling (kanji → kana).

Converting kanji to kana is not a codepoint mapping: a kanji's kana spelling
is a *lexical* property resolved against a reading dictionary, and genuinely
ambiguous readings are decided by the dictionary's segmentation.  This is
still orthography — the output is how the word is written in kana, exactly as
an IME or furigana would render it — not phonemization; no sound rules are
applied.

The reading dictionary comes from ``pykakasi`` (``pip install scriptconv[ja]``).
Importing the module is always safe; the dependency is resolved on first
conversion and a missing dictionary raises :class:`ImportError` rather than
silently returning unconverted text.
"""
from __future__ import annotations

from typing import Iterator, NamedTuple

__all__ = ["ReadingToken", "tokens", "to_hiragana", "to_katakana"]


class ReadingToken(NamedTuple):
    """One dictionary-segmented token of Japanese text and its kana readings."""
    orig: str
    hira: str
    kana: str

_kakasi = None

_HIRA = range(0x3040, 0x30A0)
_KANA = range(0x30A0, 0x3100)


def _converter():
    global _kakasi
    if _kakasi is None:
        try:
            import pykakasi
        except ImportError:
            raise ImportError(
                "kanji→kana conversion needs the reading dictionary from "
                "pykakasi — install with `pip install scriptconv[ja]`"
            ) from None
        _kakasi = pykakasi.kakasi()
    return _kakasi


def tokens(text: str) -> Iterator[ReadingToken]:
    """Iterate the dictionary's segmentation of *text* with per-token readings.

    Each token is a :class:`ReadingToken` with the original surface form and
    its hiragana and katakana readings.  This is the primitive under
    :func:`to_hiragana`/:func:`to_katakana`; use it directly when the consumer
    needs token boundaries — e.g. word segmentation (wakachigaki) or
    reading-dependent post-processing — rather than a joined string.
    """
    for t in _converter().convert(text):
        if t["orig"]:
            yield ReadingToken(t["orig"], t["hira"], t["kana"])


def to_hiragana(text: str, keep_katakana: bool = False,
                segment: bool = False) -> str:
    """Respell Japanese text in hiragana.

    Kanji are resolved to their dictionary reading; existing kana and any
    non-Japanese characters pass through.  With ``keep_katakana=True``,
    katakana tokens keep their original script (useful when katakana marks
    loanwords deliberately) instead of being folded into hiragana.  With
    ``segment=True``, dictionary tokens are joined with spaces (wakachigaki,
    the spaced orthographic mode) instead of concatenated — equivalent to
    ``scriptconv.apply(..., "wakachigaki")`` over this token stream
    (:mod:`scriptconv.conventions`).
    """
    out = []
    for tok in tokens(text):
        if keep_katakana and tok.orig and all(
                ord(c) in _KANA or not _is_japanese(c) for c in tok.orig):
            out.append(tok.orig)
        else:
            out.append(tok.hira)
    return " ".join(" ".join(out).split()) if segment else "".join(out)


def to_katakana(text: str, segment: bool = False) -> str:
    """Respell Japanese text in katakana.

    Kanji are resolved to their dictionary reading; existing kana are
    transposed to katakana and any non-Japanese characters pass through.
    With ``segment=True``, dictionary tokens are joined with spaces
    (wakachigaki) instead of concatenated.
    """
    kana = [tok.kana for tok in tokens(text)]
    return " ".join(" ".join(kana).split()) if segment else "".join(kana)


def _is_japanese(ch: str) -> bool:
    cp = ord(ch)
    return cp in _HIRA or cp in _KANA or 0x4E00 <= cp <= 0x9FFF

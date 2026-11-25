# How scriptconv finds these backends

<!-- agent-hint
covers: how scriptconv finds, imports, picks and reports the classes of this package
source: scriptconv/phonemizers/registry.py and scriptconv/phonemizers/_moved.py in scriptconv, scriptconv_copyleft/__init__.py, scriptconv_copyleft/phonemizers/__init__.py
generated: no
verify: python -m doctest docs/how-it-works.md
see: docs/backends.md, docs/phonemizers.md in scriptconv
-->

This page explains how a `Phonemizer` value in scriptconv reaches a class in
scriptconv-copyleft. This package registers nothing itself: scriptconv holds
the registry, and this package holds the classes.

## The registry row

`PHONEMIZER_REGISTRY` in `scriptconv.phonemizers.registry` maps each
`Phonemizer` member to three strings: the module, the class name, and the
scriptconv extra that installs the class. For a backend of this package, the
module starts with `scriptconv_copyleft.`:

```python
>>> import sys
>>> import scriptconv.phonemizers
>>> "scriptconv_copyleft" in sys.modules
False
>>> from scriptconv.phonemizers import Phonemizer
>>> from scriptconv.phonemizers.registry import PHONEMIZER_REGISTRY
>>> PHONEMIZER_REGISTRY[Phonemizer.ESPEAK]
('scriptconv_copyleft.phonemizers.mul', 'EspeakPhonemizer', 'espeak')

```

The first check shows that `import scriptconv` does not import this package.
These 18 members resolve to this package:

```python
>>> from scriptconv.phonemizers.registry import PHONEMIZER_REGISTRY
>>> [m.value for m, (module, _, _) in PHONEMIZER_REGISTRY.items()
...  if module.startswith("scriptconv_copyleft.")]
['espeak', 'espeak_lt_accent', 'transphone', 'misaki', 'misaki_en', 'misaki_ja', 'misaki_zh', 'misaki_ko', 'misaki_vi', 'cotovia', 'ahotts', 'hebrew_ipa', 'tltk', 'g2pfa', 'pykakasi', 'openjtalk_prosody', 'g2pk', 'kog2p']

```

## The import on first use

`get_phonemizer_class(member)` imports the module of the row and returns the
class. `get_phonemizer(member, alphabet, model, **kwargs)` does the same, then
builds an instance:

- It gives `alphabet` to the constructor when the constructor has an
  `alphabet` parameter. The default is `Alphabet.IPA`, so a backend that
  cannot write IPA, such as `pykakasi`, needs an explicit alphabet.
- It gives `model` to the first of the parameters `model`, `engine` or
  `register` that the constructor has. Cotovía takes `model`, and AhoTTS takes
  `engine`.
- It gives the other keyword arguments to the constructor, for example
  `prefer_espyak=True` for espeak.

When the import fails, `get_phonemizer` raises an `ImportError` that names the
scriptconv extra of the row:

```python
from scriptconv.phonemizers import Phonemizer, get_phonemizer

get_phonemizer(Phonemizer.MISAKI_EN)
# ImportError: phonemizer 'misaki_en' needs a missing backing package — install with `pip install scriptconv[misaki]`
```

Each class also imports its engine on first use. When the engine is missing,
the class raises an `ImportError` with an install command.

## The language defaults

`phonemizer_for_lang(lang, alphabet)` picks a backend when the caller names
none. Two backends of this package are in its chains. Cotovía is the first
Galician candidate, and only for the Cotovía alphabet. espeak is the last
candidate for Galician and Russian:

```python
>>> from scriptconv.phonemizers import Alphabet
>>> from scriptconv.phonemizers.registry import LANG_DEFAULTS, phonemizer_for_lang
>>> [m.value for m in LANG_DEFAULTS["gl"]]
['cotovia', 'orthography2ipa', 'espeak']
>>> type(phonemizer_for_lang("gl", alphabet=Alphabet.COTOVIA)).__name__
'CotoviaPhonemizer'

```

A language with no row in `LANG_DEFAULTS` gets orthography2ipa when that
package supports the language and the alphabet is IPA. Every other case gets
espeak, except Arabic, which never leaves its own row. So espeak is the last
resort for most languages, and `scriptconv[espeak]` is the extra to install
for it.

## Deprecated import paths in scriptconv

scriptconv also gives each class of this package at a deprecated path in
scriptconv, for example `scriptconv.phonemizers.mul.EspeakPhonemizer`. The first use
of such a path warns with a `DeprecationWarning`:

```python
from scriptconv.phonemizers.mul import EspeakPhonemizer
# DeprecationWarning: scriptconv.phonemizers.mul.EspeakPhonemizer is deprecated and will be removed in scriptconv 0.1.0; import it from scriptconv_copyleft.phonemizers.mul (`pip install scriptconv[espeak]`)
```

`scriptconv.phonemizers._moved.REMOVAL_VERSION` names the scriptconv release
that removes these paths. Import from `scriptconv_copyleft.phonemizers` or call
`get_phonemizer`.

## The identity of a backend

`identity(lang)` returns the `Phonemizer` value, the distribution and the
version of the engine, the resolved language and a revision hash. The engine
is the distribution that gives the phonemes. When the engine is code inside
this package, the distribution is `scriptconv-copyleft`:

```python
>>> from scriptconv.phonemizers import Phonemizer, get_phonemizer
>>> get_phonemizer(Phonemizer.HEBREW_IPA).identity("he").distribution
'scriptconv-copyleft'
>>> get_phonemizer(Phonemizer.KOG2PK).identity("ko").distribution
'scriptconv-copyleft'

```

`kog2p` reports `kog2p` when a separate `kog2p` distribution is installed,
because that distribution then runs in place of the copy in this package. The
revision hash covers the code of scriptconv and of this package on the path of
the backend. The scriptconv
[phonemizer page](https://github.com/TigreGotico/scriptconv/blob/dev/docs/phonemizers.md)
explains the contract, the registry and the revision.

---
[← Prev](getting-started.md) · [Home](index.md) · [Next →](backends.md)

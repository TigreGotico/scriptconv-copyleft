# Backend reference

<!-- agent-hint
covers: every backend of this package with its Phonemizer value, class, module, scriptconv extra, languages, alphabets, parameters, licence and first-use downloads
source: scriptconv_copyleft/phonemizers/*.py, scriptconv_copyleft/readings.py, pyproject.toml, scriptconv/phonemizers/registry.py in scriptconv
generated: no
verify: python -m doctest docs/backends.md && python -c "import re,sys; from scriptconv.phonemizers.registry import PHONEMIZER_REGISTRY as R; rows={(v,(m,c,e)) for v,c,m,e in re.findall(r'^\| \`(\w+)\` \| \`(\w+)\` \| \`([\w.]+)\` \| \`([\w-]+)\` \|', open('docs/backends.md').read(), re.M)}; want={(p.value,t) for p,t in R.items() if t[0].startswith('scriptconv_copyleft.')}; sys.exit(rows!=want)"
see: docs/licences.md, docs/backends.md in scriptconv
-->

This page lists every backend that scriptconv-copyleft holds. For each one it
gives the extra to install, the languages, the alphabets, the parameters, the
copyleft item that puts it in this package, and what it downloads on first
use.

## The table

Install a backend with its scriptconv extra, for example
`uv pip install --prerelease=allow "scriptconv[th]"`. The scriptconv extra
installs this package with the extra of the same name, which holds the
dependencies of the backend.

| `Phonemizer` value | Class | Module | scriptconv extra | Languages |
| --- | --- | --- | --- | --- |
| `espeak` | `EspeakPhonemizer` | `scriptconv_copyleft.phonemizers.mul` | `espeak` | the 137 espeak-ng voices in `ESPEAK_LANGS` |
| `espeak_lt_accent` | `EspeakLithuanianAccentPhonemizer` | `scriptconv_copyleft.phonemizers.lt` | `espeak` | `lt` |
| `transphone` | `TransphonePhonemizer` | `scriptconv_copyleft.phonemizers.mul` | `transphone` | the 7,416 ISO 639-3 codes in `TRANSPHONE_LANGS` |
| `misaki` | `MisakiPhonemizer` | `scriptconv_copyleft.phonemizers.mul` | `misaki` | `en-US`, `en-GB`, `ja`, `zh`, `ko`, `vi` |
| `misaki_en` | `MisakiEnPhonemizer` | `scriptconv_copyleft.phonemizers.mul` | `misaki` | `en-US`, `en-GB` |
| `misaki_ja` | `MisakiJaPhonemizer` | `scriptconv_copyleft.phonemizers.mul` | `misaki` | `ja` |
| `misaki_zh` | `MisakiZhPhonemizer` | `scriptconv_copyleft.phonemizers.mul` | `misaki` | `zh` |
| `misaki_ko` | `MisakiKoPhonemizer` | `scriptconv_copyleft.phonemizers.mul` | `misaki` | `ko` |
| `misaki_vi` | `MisakiViPhonemizer` | `scriptconv_copyleft.phonemizers.mul` | `misaki` | `vi` |
| `cotovia` | `CotoviaPhonemizer` | `scriptconv_copyleft.phonemizers.gl` | `gl` | `gl` |
| `ahotts` | `AhoTTSPhonemizer` | `scriptconv_copyleft.phonemizers.eu` | `eu` | `eu`, `es` |
| `hebrew_ipa` | `HebrewIPAPhonemizer` | `scriptconv_copyleft.phonemizers.he` | `he` | `he` |
| `tltk` | `TLTKPhonemizer` | `scriptconv_copyleft.phonemizers.th` | `th` | `th` |
| `g2pfa` | `PersianPhonemizer` | `scriptconv_copyleft.phonemizers.fa` | `fa` | `fa` |
| `pykakasi` | `PyKakasiPhonemizer` | `scriptconv_copyleft.phonemizers.ja` | `ja-phonemizers` | `ja` |
| `openjtalk_prosody` | `OpenJTalkProsodyPhonemizer` | `scriptconv_copyleft.phonemizers.ja_prosody` | `ja-phonemizers` | `ja` |
| `g2pk` | `G2PKPhonemizer` | `scriptconv_copyleft.phonemizers.ko` | `ko` | `ko` |
| `kog2p` | `KoG2PPhonemizer` | `scriptconv_copyleft.phonemizers.ko` | `ko` | `ko` |

Each backend matches the requested language tag to its own list, so `pt-BR`
or `en-GB` find the nearest voice. The `misaki` and `ko` extras of this package
install their engines on Python 3.12 and older only: misaki declares
`Requires-Python <3.13`, and python-mecab-ko has no wheel for Python 3.13.

## Downloads on first use

Three backends download files the first time they run. The others use data
that their wheels hold.

| Backend | Download | Size on disk | Destination |
| --- | --- | --- | --- |
| `transphone` | the phonepiece model `latest` and the transphone model `042801_base`, from GitHub releases of xinjli | 138 MB and 86 MB | `phonepiece/data/model` and `transphone/data/model` in site-packages |
| `misaki`, `misaki_en` with English, `misaki_vi` | the spaCy model `en_core_web_sm`, through `spacy.cli.download` | 15 MB | site-packages, as a package |
| `g2pk` | the NLTK `cmudict` corpus, when NLTK does not find it | 4.6 MB (the 0.9 MB zip and its 3.7 MB unpacked copy) | `~/nltk_data` |

## espeak

`EspeakPhonemizer` runs the espeak-ng program when it is on `PATH`, and
espyak, the Python port, when it is not. `prefer_espyak=True` runs espyak in
all cases. The output is IPA with stress marks.

```python
>>> from scriptconv.phonemizers import Phonemizer, get_phonemizer
>>> get_phonemizer(Phonemizer.ESPEAK, prefer_espyak=True).phonemize_string("Hello world", "en-GB")
'həlˈəʊ wˈɜːld'

```

`get_lang` maps `en-GB` to the `en-gb-x-rp` voice, `zh` to `cmn`, and
`zh-HK` and `zh-MO` to `yue`.

Licence: espyak is GPL-3.0-or-later, and the espeak-ng program is
GPL-3.0-or-later. Downloads: none.

## espeak_lt_accent

`EspeakLithuanianAccentPhonemizer` gives Lithuanian espeak-ng IPA with the
three pitch accents: `ˈ` for the acute, `ˌ` for the circumflex and `ˋ` for the
short accent. A stress dictionary of 189,262 words places the accent. A word
that is not in the dictionary keeps the stress of espeak-ng.

```python
>>> from scriptconv.phonemizers import Phonemizer, get_phonemizer
>>> get_phonemizer(Phonemizer.ESPEAK_LT_ACCENT).phonemize_string("Laba diena, Lietuva!", "lt")
'l̩ˈaba dʲieˋna, ɭietuˋva!'

```

The parameters `dictionary_path`, `letters_path` and `vocatives_path` replace
the stress dictionary, the letter names and the nouns of direct address. An
empty vocatives file turns off the vocative accent rule. `prefer_espyak`
works as for espeak.

The code and data come from Reginutė by Robertas Tarasevičius
(github.com/RobertasTa/reginute, commit 328d98d). Licence: the module and the
letter and vocative files are GPL-3.0-only. The stress dictionary is
CC-BY-4.0 AND GPL-3.0-only. Downloads: none; the data is in this package.

## transphone

`TransphonePhonemizer` gives approximate IPA for the ISO 639-3 codes of
transphone. It has no parameters. It builds one transphone tokenizer for each
language on first use:

```python
from scriptconv.phonemizers import Phonemizer, get_phonemizer

get_phonemizer(Phonemizer.TRANSPHONE).phonemize_string("hello world", "eng")
# 'hʌlow wɹ̩ld'
```

The `transphone` extra also installs jieba, pypinyin, unidic-lite and pip.
transphone installs a missing package with pip during a call, and the extra
installs those packages first.

Licence: transphone pulls cmudict (GPL-3.0-or-later) and Unidecode
(GPL-2.0-or-later), and phonepiece pulls iso-639 (AGPL-3.0). Downloads: two
models, see [Downloads on first use](#downloads-on-first-use).

## misaki

misaki is the G2P of the Kokoro voices (github.com/hexgrad/misaki).
`MisakiPhonemizer` takes all six languages, and each subclass takes one
language. misaki builds the G2P of a language on first use, which can take
some seconds.

```python
>>> from scriptconv.phonemizers import Alphabet, Phonemizer, get_phonemizer
>>> get_phonemizer(Phonemizer.MISAKI_ZH).phonemize_string("你好", "zh")
'ni↓xau↓'
>>> get_phonemizer(Phonemizer.MISAKI_ZH, alphabet=Alphabet.BOPOMOFO).phonemize_string("你好", "zh")
Warning: en_callable is None, so English may be removed
'ㄋㄧ2ㄏㄠ3'
>>> get_phonemizer(Phonemizer.MISAKI_KO, alphabet=Alphabet.HANGUL).phonemize_string("한국말", "ko")
'한궁말'
>>> get_phonemizer(Phonemizer.MISAKI_JA).phonemize_string("日本語", "ja")
'ɲiʔpoŋɡo'

```

```python
from scriptconv.phonemizers import Phonemizer, get_phonemizer

get_phonemizer(Phonemizer.MISAKI_EN).phonemize_string("Hello world", "en-US")
# 'həlˈO wˈɜɹld'
```

The alphabets:

- `misaki_zh` writes IPA with tone marks, or bopomofo with tone digits for
  `Alphabet.BOPOMOFO`. misaki prints a warning on standard output when it
  builds the bopomofo G2P.
- `misaki_ko` writes Hangul with the sound changes applied, so it takes only
  `Alphabet.HANGUL`. Pass that alphabet to `get_phonemizer`, because its
  default is IPA.
- The other languages write IPA. English `en-GB` loads the British lexicon of
  misaki, and `en-US` the American one.

The Japanese reader of misaki is cutlet on fugashi. misaki imports the
`pyopenjtalk` module, and the `misaki` extra installs it from
pyopenjtalk-plus, but the cutlet reader does not call it.

For `misaki_vi`, the `misaki` extra installs the `vi` extra of misaki, which
pulls underthesea, and vietnam-number, which the Vietnamese text cleaner of
misaki imports without a declaration.

Licence: misaki is Apache-2.0, but its English module pulls phonemizer-fork
(GPL-3.0-or-later) and espeakng-loader, which bundles libespeak-ng. The
Vietnamese module pulls underthesea (Apache-2.0) and vietnam-number
(GPL-3.0-or-later). Downloads:
the spaCy English model, see
[Downloads on first use](#downloads-on-first-use).

## cotovia

`CotoviaPhonemizer` is Galician G2P through pycotovia, a Python port of the
Cotovía engine. The class default is `Alphabet.COTOVIA`, the native notation
of Cotovía, and `Alphabet.IPA` converts it. `get_phonemizer` gives IPA unless
you pass `alphabet=Alphabet.COTOVIA`. `model="stress"` writes the Cotovía
notation with `^` after each stressed vowel:

```python
>>> from scriptconv.phonemizers import Alphabet, Phonemizer, get_phonemizer
>>> get_phonemizer(Phonemizer.COTOVIA).phonemize_string("Ola mundo", "gl")
'ola mundo'
>>> get_phonemizer(Phonemizer.COTOVIA, alphabet=Alphabet.COTOVIA).phonemize_string("Ola mundo", "gl")
'ola mundo '
>>> get_phonemizer(Phonemizer.COTOVIA, model="stress").phonemize_string("Ola mundo", "gl")
'o^la mu^ndo '

```

Licence: pycotovia is GPL-3.0-or-later. Downloads: none.

## ahotts

`AhoTTSPhonemizer` is Basque and Spanish G2P through ahotts-g2p, a Python
port of the AhoTTS engine. The output is one character for each phoneme. The
`engine` parameter, or `model` in `get_phonemizer`, selects the variant:

| `engine` | Variant |
| --- | --- |
| `modern` | the default; the build of the HiTZ StyleTTS2 Basque voice |
| `classic` | the original AhoTTS engine of the HiTZ VITS voices |
| `northern` | the Northern Basque dialect; Basque only |

```python
>>> from scriptconv.phonemizers import Phonemizer, get_phonemizer
>>> get_phonemizer(Phonemizer.AHOTTS).phonemize_string("Kaixo mundua", "eu")
'kajʃO mundUa'
>>> get_phonemizer(Phonemizer.AHOTTS).phonemize_string("Hola mundo", "es")
'Ola mUndo'

```

The `northern` engine raises `ValueError` for Spanish. Licence: ahotts-g2p is
GPL-3.0-or-later. Downloads: none.

## hebrew_ipa

`HebrewIPAPhonemizer` reads Hebrew text with niqqud and gives Modern Israeli
Hebrew IPA with the stress mark. It adds no niqqud, so text without niqqud
gives consonants without vowels. In scriptconv, the diacritize stage
(Nakdimon or phonikud) runs before it.

```python
>>> from scriptconv.phonemizers import Phonemizer, get_phonemizer
>>> get_phonemizer(Phonemizer.HEBREW_IPA).phonemize_string("שָׁלוֹם עוֹלָם", "he")
'ʃˈalom ʔˈolam'

```

The backend is pure Python and needs no extra of this package. The scriptconv
`he` extra installs this package with phonikud. Licence: the module is
ported from Piper (OHF-Voice/piper1-gpl), so it is GPL-3.0-or-later.
Downloads: none.

## tltk

`TLTKPhonemizer` gives Thai IPA from TLTK, with a tone digit after each
syllable: 1 mid, 2 low, 3 falling, 4 high and 5 rising. TLTK segments the
words. The backend reads numbers itself with unicode-rbnf, so it owns the
`normalize` stage:

```python
>>> from scriptconv.phonemizers import Phonemizer, get_phonemizer
>>> get_phonemizer(Phonemizer.TLTK).phonemize_string("ราคา 25 บาท", "th")
'raː1kʰaː1 jiː3 sip2 haː3 baːt2'

```

Digits that follow a letter with no space, as in `โควิด19` or `A4`, are
dropped with a warning.

Licence: the module is ported from Piper (OHF-Voice/piper1-gpl), so it is
GPL-3.0-or-later. TLTK states BSD-3-Clause in its metadata, but its wheel
ships a GPL-3.0 text, so this package treats it as GPL. TLTK also pulls gensim
(LGPL-2.1-only). Downloads: none.

## g2pfa

`PersianPhonemizer` is Persian G2P through persian_phonemizer, which runs hazm
and a spaCy model that it holds. Building the backend takes some seconds.

```python
from scriptconv.phonemizers import Phonemizer, get_phonemizer

get_phonemizer(Phonemizer.G2PFA).phonemize_string("سلام دنیا", "fa")
# 'sælɒːme doniːɒː'
```

The class accepts `Alphabet.IPA` and `Alphabet.ERAAB`, but both give IPA
([#15](https://github.com/TigreGotico/scriptconv-copyleft/issues/15)).

Licence: hazm 0.10 and 0.11 require gensim (LGPL-2.1-only), and the extra
admits them with `hazm>=0.10`. Downloads: none.

## pykakasi

`PyKakasiPhonemizer` gives the dictionary reading of Japanese text in Hepburn
romaji, katakana or hiragana. It does not write IPA, so pass an alphabet to
`get_phonemizer`:

```python
>>> from scriptconv.phonemizers import Alphabet, Phonemizer, get_phonemizer
>>> get_phonemizer(Phonemizer.PYKAKASI, alphabet=Alphabet.HEPBURN).phonemize_string("日本語", "ja")
'nihongo'
>>> get_phonemizer(Phonemizer.PYKAKASI, alphabet=Alphabet.KANA).phonemize_string("日本語", "ja")
'ニホンゴ'

```

Licence: pykakasi is GPL-3.0-or-later. Downloads: none.

## openjtalk_prosody

`OpenJTalkProsodyPhonemizer` gives Japanese IPA from OpenJTalk with the
prosody marks of Piper: `↑` accent rise, `↓` accent fall, `#` accent phrase
boundary, `,` pause, and `.` or `?` at the end of a sentence.

```python
>>> from scriptconv.phonemizers import Phonemizer, get_phonemizer
>>> get_phonemizer(Phonemizer.OPENJTALK_PROSODY).phonemize_string("今日は良い天気ですね。", "ja")
'kʲo↓owa#jo↓i#te↓ɴkidesɯne.'

```

`drop_devoiced_vowels=True`, the default, writes a devoiced vowel as its
voiced vowel. The backend runs only when the `pyopenjtalk` module comes from
pyopenjtalk-plus and onnxruntime imports. Other installs give other readings,
so the backend refuses them with `ImportError`.

Licence: the IPA map and the code around it are ported from Piper
(OHF-Voice/piper1-gpl), so the module is GPL-3.0-or-later. pyopenjtalk-plus is
MIT, and its dictionary is BSD-3-Clause. Downloads: none; pyopenjtalk-plus
holds the dictionary.

## g2pk

`G2PKPhonemizer` is Korean G2P through g2pk, which applies the Korean sound
changes in Hangul. `Alphabet.IPA`, the default, converts the Hangul to IPA, and
`Alphabet.HANGUL` keeps it:

```python
>>> from scriptconv.phonemizers import Alphabet, Phonemizer, get_phonemizer
>>> get_phonemizer(Phonemizer.G2PK).phonemize_string("한국말", "ko")
'häŋɡuŋmäl'
>>> get_phonemizer(Phonemizer.G2PK, alphabet=Alphabet.HANGUL).phonemize_string("한국말", "ko")
'한궁말'

```

The parameters `descriptive`, `group_vowels` and `to_syl` go to g2pk and are
`True` by default.

Licence: g2pk is Apache-2.0, but it pulls KoNLPy (GPL-3.0-or-later).
Downloads: the NLTK `cmudict` corpus, see
[Downloads on first use](#downloads-on-first-use).

## kog2p

`KoG2PPhonemizer` is Korean G2P through KoG2P (scarletcho/KoG2P). It uses an
installed `kog2p` distribution when there is one, and the copy in
`scriptconv_copyleft/phonemizers/_vendored/kog2p` when there is not. The output
is Hangul compatibility jamo with the sound changes applied, whatever
alphabet you pass
([#16](https://github.com/TigreGotico/scriptconv-copyleft/issues/16)):

```python
>>> from scriptconv.phonemizers import Phonemizer, get_phonemizer
>>> get_phonemizer(Phonemizer.KOG2PK).phonemize_string("한국말", "ko")
'ㅎㅏㄴㄱㅜㅇㅁㅏㄹ'

```

scriptconv never picks KoG2P for a language. Licence: the KoG2P code is
GPL-3.0-only. Downloads: none.

## Japanese readings

`scriptconv_copyleft.readings` respells Japanese kanji in kana with the
pykakasi dictionary. `scriptconv.readings` gives the same functions, and
imports them from this package on first use. Install them with
`uv pip install --prerelease=allow "scriptconv[ja]"`.

```python
>>> from scriptconv_copyleft.readings import to_hiragana, to_katakana, tokens
>>> to_hiragana("日本語を話す")
'にほんごをはなす'
>>> to_katakana("日本語を話す")
'ニホンゴヲハナス'
>>> list(tokens("日本語"))
[ReadingToken(orig='日本語', hira='にほんご', kana='ニホンゴ')]

```

`to_hiragana(text, keep_katakana=False, segment=False)` keeps katakana words
with `keep_katakana=True`, and `segment=True` puts a space between the tokens
of the dictionary. `to_katakana(text, segment=False)` takes `segment` too. The
scriptconv [readings page](https://github.com/TigreGotico/scriptconv/blob/dev/docs/readings.md)
explains where the readings fit. Licence: pykakasi is GPL-3.0-or-later.

---

[Index](index.md) · Previous: [How it works](how-it-works.md) · Next: [Licences](licences.md)

# scriptconv-copyleft

The scriptconv phonemizer backends whose own code or whose dependencies are under a copyleft licence (GPL, LGPL or AGPL).

## Where this fits

[scriptconv](https://github.com/TigreGotico/scriptconv) is the text conversion library. Its wheel holds only Apache-2.0 code. Each backend in this package has a copyleft licence somewhere in its chain, so it ships here instead.

scriptconv keeps the registry. A backend keeps its `Phonemizer` value and its routing entry in scriptconv, and scriptconv imports the class from this package only when a caller asks for that backend. The scriptconv extra of each backend installs this package, so the install command does not change:

```bash
pip install scriptconv[espeak]
```

```python
from scriptconv.phonemizers import Phonemizer, get_phonemizer

get_phonemizer(Phonemizer.ESPEAK).phonemize_string("olá", "pt")
```

This package depends on scriptconv. scriptconv never imports this package when it is imported itself.

## Backends

| `Phonemizer` value | Class | Module | Copyleft item in the chain |
| --- | --- | --- | --- |
| `espeak` | `EspeakPhonemizer` | `scriptconv_copyleft.phonemizers.mul` | espyak (GPL-3.0-or-later), the espeak-ng binary (GPL-3.0-or-later) |
| `misaki`, `misaki_en`, `misaki_ja`, `misaki_zh`, `misaki_ko`, `misaki_vi` | `MisakiPhonemizer` and its five subclasses | `scriptconv_copyleft.phonemizers.mul` | phonemizer-fork (GPL-3.0-or-later), espeakng-loader (bundles libespeak-ng) |
| `transphone` | `TransphonePhonemizer` | `scriptconv_copyleft.phonemizers.mul` | cmudict (GPL-3.0-or-later), unidecode (GPL-2.0-or-later), iso-639 (AGPL-3.0) |
| `cotovia` | `CotoviaPhonemizer` | `scriptconv_copyleft.phonemizers.gl` | pycotovia (GPL-3.0-or-later) |
| `ahotts` | `AhoTTSPhonemizer` | `scriptconv_copyleft.phonemizers.eu` | ahotts-g2p (GPL-3.0-or-later) |
| `g2pfa` | `PersianPhonemizer` | `scriptconv_copyleft.phonemizers.fa` | gensim (LGPL-2.1-only), through hazm |
| `g2pk` | `G2PKPhonemizer` | `scriptconv_copyleft.phonemizers.ko` | konlpy (GPL-3.0-or-later) |
| `kog2p` | `KoG2PPhonemizer` | `scriptconv_copyleft.phonemizers.ko` | the vendored KoG2P code (GPL-3.0-only) |
| `pykakasi` | `PyKakasiPhonemizer` | `scriptconv_copyleft.phonemizers.ja` | pykakasi (GPL-3.0-or-later) |
| `espeak_lt_accent` | `EspeakLithuanianAccentPhonemizer` | `scriptconv_copyleft.phonemizers.lt` | the module itself, ported from Reginutė (GPL-3.0-only); the espeak-ng binary (GPL-3.0-or-later) |

`espeak_lt_accent` gives Lithuanian espeak-ng IPA with the three pitch accents (`ˈ`, `ˌ`, `ˋ`) from a stress dictionary of 189,262 words. It needs the `espeak` extra and the espeak-ng binary. The code and the dictionary come from Reginutė by Robertas Tarasevičius (github.com/RobertasTa/reginute, commit 328d98d, `phonemize_lithuanian.py`). The phonemes come from espeak-ng (github.com/espeak-ng/espeak-ng).

misaki's Japanese module (`misaki_ja`, and `misaki` with `ja`) imports the `pyopenjtalk` module. The `misaki` extra installs it from pyopenjtalk-plus with onnxruntime (github.com/tsukumijima/pyopenjtalk-plus, MIT). pyopenjtalk-plus ships wheels and bundles the OpenJTalk dictionary, so it installs with no compiler and works offline from the first call. pyopenjtalk installs the same module, so no extra of this package installs it. misaki's default Japanese reader (cutlet, on fugashi) does not call pyopenjtalk, so the OpenJTalk distribution does not change its phonemes.

`scriptconv_copyleft.readings` holds the Japanese kanji-to-kana respelling (`tokens`, `to_hiragana`, `to_katakana`), which needs pykakasi.

Each backend's own dependencies install with its extra, for example `pip install scriptconv-copyleft[espeak]`.

## Licence

The package holds code and data under three licences. The SPDX expression is `Apache-2.0 AND GPL-3.0-only AND CC-BY-4.0`.

| Files | Licence | Notice |
| --- | --- | --- |
| `scriptconv_copyleft/phonemizers/_vendored/kog2p/` | GPL-3.0-only | `LICENSE.md` and `COPYING` in that directory. Upstream (scarletcho/KoG2P) ships the GPL version 3 text and states no "or later" grant. |
| `scriptconv_copyleft/phonemizers/lt.py` | GPL-3.0-only | Ported from Reginutė (RobertasTa/reginute), whose code is GPL-3.0-only. The module docstring names its source file and commit. The GPL text is `_vendored/reginute/COPYING`. |
| `scriptconv_copyleft/phonemizers/_vendored/reginute/lt_kirciai.tsv` | CC-BY-4.0 AND GPL-3.0-only | `LICENSE`, `COPYING` and `SOURCE` in that directory. The entries come from the LIEPA corpus annotation (Vilnius University) and the g2p-lt-lexicon of Arunas Smaliukas, both CC-BY-4.0. Reginutė's manual corrections are GPL-3.0-only. |
| `scriptconv_copyleft/phonemizers/_vendored/reginute/lt_raides.tsv`, `lt_kreipiniai.tsv` | GPL-3.0-only | `COPYING` and `SOURCE` in that directory: Reginutė's own work. |
| every other file | Apache-2.0 | `LICENSE` |

The dependencies of each backend keep their own licences. A program that installs and uses a backend must follow the licence of that backend's dependencies.

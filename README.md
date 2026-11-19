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
| `hebrew_ipa` | `HebrewIPAPhonemizer` | `scriptconv_copyleft.phonemizers.he` | the module itself, ported from piper1-gpl (GPL-3.0-or-later) |
| `openjtalk_prosody` | `OpenJTalkProsodyPhonemizer` | `scriptconv_copyleft.phonemizers.ja_prosody` | the module itself, ported from piper1-gpl (GPL-3.0-or-later) |
| `tltk` | `TLTKPhonemizer` | `scriptconv_copyleft.phonemizers.th` | the module itself, ported from piper1-gpl (GPL-3.0-or-later); tltk, treated as GPL because its licence statements disagree |

`espeak_lt_accent` gives Lithuanian espeak-ng IPA with the three pitch accents (`ˈ`, `ˌ`, `ˋ`) from a stress dictionary of 189,262 words. It needs the `espeak` extra and the espeak-ng binary. The code and the dictionary come from Reginutė by Robertas Tarasevičius (github.com/RobertasTa/reginute, commit 328d98d, `phonemize_lithuanian.py`). The phonemes come from espeak-ng (github.com/espeak-ng/espeak-ng).

`hebrew_ipa` reads Hebrew text that carries niqqud and gives Modern Israeli Hebrew IPA with the stress mark. It adds no niqqud, so the diacritize stage of scriptconv (Nakdimon or phonikud) runs before it. The rules were written by Michael Hansen for Piper (OHF-Voice/piper1-gpl, `src/piper/hebrew/hebrew_ipa.py`).

`openjtalk_prosody` gives Japanese IPA from OpenJTalk, with the accent rise `↑`, the accent fall `↓`, the accent phrase boundary `#`, the pause `,` and the sentence ends `.` and `?`. The engine is OpenJTalk through pyopenjtalk-plus (MIT; dictionary BSD-3-Clause), and the accent marks follow ESPnet's `pyopenjtalk_g2p_prosody` (Apache-2.0). The IPA map was written for Piper (`src/piper/phonemize_japanese.py`). It needs the `ja-phonemizers` extra. It runs only when the `pyopenjtalk` module comes from pyopenjtalk-plus and onnxruntime imports, through the engine check of `scriptconv.phonemizers.openjtalk_engine`, because other installs give other readings.

`tltk` gives Thai IPA from TLTK (github.com/attapol/tltk), with a tone digit from 1 to 5 after each syllable. It reads numbers itself with unicode-rbnf (MIT). It drops digits that follow a letter with no space, for example `โควิด19` or `A4`, and logs a warning. The wrapper was written for Piper (`src/piper/phonemize_thai.py`). It needs the `th` extra.

misaki's Japanese module (`misaki_ja`, and `misaki` with `ja`) imports the `pyopenjtalk` module. The `misaki` extra installs it from pyopenjtalk-plus with onnxruntime (github.com/tsukumijima/pyopenjtalk-plus, MIT). pyopenjtalk-plus ships wheels and bundles the OpenJTalk dictionary, so it installs with no compiler and works offline from the first call. pyopenjtalk installs the same module, so no extra of this package installs it. misaki's default Japanese reader (cutlet, on fugashi) does not call pyopenjtalk, so the OpenJTalk distribution does not change its phonemes.

`scriptconv_copyleft.readings` holds the Japanese kanji-to-kana respelling (`tokens`, `to_hiragana`, `to_katakana`), which needs pykakasi.

Each backend's own dependencies install with its extra, for example `pip install scriptconv-copyleft[espeak]`.

## Licence

The package holds code and data under four licences. The SPDX expression is `Apache-2.0 AND GPL-3.0-only AND GPL-3.0-or-later AND CC-BY-4.0`.

| Files | Licence | Notice |
| --- | --- | --- |
| `scriptconv_copyleft/phonemizers/_vendored/kog2p/` | GPL-3.0-only | `LICENSE.md` and `COPYING` in that directory. Upstream (scarletcho/KoG2P) ships the GPL version 3 text and states no "or later" grant. |
| `scriptconv_copyleft/phonemizers/lt.py` | GPL-3.0-only | Ported from Reginutė (RobertasTa/reginute), whose code is GPL-3.0-only. The module docstring names its source file and commit. The GPL text is `_vendored/reginute/COPYING`. |
| `scriptconv_copyleft/phonemizers/_vendored/reginute/lt_kirciai.tsv` | CC-BY-4.0 AND GPL-3.0-only | `LICENSE`, `COPYING` and `SOURCE` in that directory. The entries come from the LIEPA corpus annotation (Vilnius University) and the g2p-lt-lexicon of Arunas Smaliukas, both CC-BY-4.0. Reginutė's manual corrections are GPL-3.0-only. |
| `scriptconv_copyleft/phonemizers/_vendored/reginute/lt_raides.tsv`, `lt_kreipiniai.tsv` | GPL-3.0-only | `COPYING` and `SOURCE` in that directory: Reginutė's own work. |
| `scriptconv_copyleft/phonemizers/he.py`, `ja_prosody.py`, `th.py` | GPL-3.0-or-later | Ported from OHF-Voice/piper1-gpl, which is GPL-3.0-or-later. Each module docstring names its source file and commit. The GPL text is `_vendored/reginute/COPYING`. |
| every other file | Apache-2.0 | `LICENSE` |

The dependencies of each backend keep their own licences. A program that installs and uses a backend must follow the licence of that backend's dependencies.

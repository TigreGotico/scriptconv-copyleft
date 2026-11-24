# Licences

<!-- agent-hint
covers: the copyleft licence of each backend, why it puts the backend here, and the licence of each file
source: pyproject.toml (license, license-files), LICENSE, scriptconv_copyleft/phonemizers/_vendored/kog2p/LICENSE.md, scriptconv_copyleft/phonemizers/_vendored/reginute/SOURCE, the docstrings of lt.py, he.py, ja_prosody.py, th.py
generated: no
verify: python -c "import os,re,sys,tomllib; b=chr(96); page=open('docs/licences.md').read(); spdx=tomllib.load(open('pyproject.toml','rb'))['project']['license']; paths=re.findall(b+'(scriptconv_copyleft/[^'+b+']+)'+b, page); sys.exit(not (b+spdx+b in page and paths and all(os.path.exists(p) for p in paths)))"
see: docs/backends.md, README.md in scriptconv
-->

This page states the licence that puts each backend in scriptconv-copyleft,
and the licence of each file in the package. It is a summary of the licence
files, not legal advice.

## Why this package exists

The scriptconv wheel holds only permissive code: Apache-2.0, MIT and the
CMUdict licence. Its extras pull no copyleft distribution of their own, except
`distance` and `num2words`, which the scriptconv
[Licensing section](https://github.com/TigreGotico/scriptconv/blob/dev/README.md#licensing)
explains. A backend comes to this package when its own code, or a dependency
of its engine, is under the GPL, the LGPL or the AGPL. scriptconv keeps the
`Phonemizer` value and the registry row, and its extra installs this package.
So a caller who installs `scriptconv[espeak]` gets the espeak backend.

A program that installs a backend and uses it must follow the licences of the
code of that backend and of its dependencies.

## Backends with copyleft code in this package

| Backend | Code | Licence |
| --- | --- | --- |
| `espeak_lt_accent` | `lt.py` and the Lithuanian data, from Reginutė | GPL-3.0-only, and CC-BY-4.0 for the dictionary sources |
| `hebrew_ipa`, `openjtalk_prosody` | `he.py` and `ja_prosody.py`, from Piper | GPL-3.0-or-later |
| `kog2p` | the vendored KoG2P code | GPL-3.0-only |

The Piper modules are ports of files of OHF-Voice/piper1-gpl, which is
GPL-3.0-or-later. Each module docstring names its source file and commit.

`tltk` has both kinds of item. Its module `th.py` is a port from Piper, so it
is GPL-3.0-or-later. TLTK, its engine, states BSD-3-Clause in its metadata and
README, but its wheel ships a GPL-3.0 text, and its repository reports
LGPL-3.0. Because the statements disagree, this package treats TLTK as GPL.
TLTK also pulls gensim, which is LGPL-2.1-only.

## Backends with a copyleft dependency

These extras of this package install a copyleft distribution directly:

| Backend | Dependency | Licence |
| --- | --- | --- |
| `espeak`, `espeak_lt_accent` | espyak, and the espeak-ng program when it is installed | GPL-3.0-or-later |
| `cotovia` | pycotovia | GPL-3.0-or-later |
| `ahotts` | ahotts-g2p | GPL-3.0-or-later |
| `pykakasi` and the Japanese readings | pykakasi | GPL-3.0-or-later |

These engines are under a permissive licence, but they pull a copyleft
distribution:

| Backend | Engine and its copyleft dependencies | Licence of the dependencies |
| --- | --- | --- |
| `misaki`, `misaki_*` | misaki pulls phonemizer-fork, and espeakng-loader, which bundles libespeak-ng | GPL-3.0-or-later |
| `transphone` | transphone pulls cmudict and Unidecode, and phonepiece pulls iso-639 | GPL-3.0-or-later, GPL-2.0-or-later, AGPL-3.0 |
| `g2pfa` | hazm 0.10 and 0.11 pull gensim | LGPL-2.1-only |
| `g2pk` | g2pk pulls KoNLPy | GPL-3.0-or-later |

hazm 0.12 and later make gensim optional, but the `fa` extra admits hazm 0.10
and 0.11.

## The files of this package

The SPDX expression of the package is
`Apache-2.0 AND GPL-3.0-only AND GPL-3.0-or-later AND CC-BY-4.0`. Every file
is Apache-2.0, with the notice in `LICENSE`, except these:

| Files | Licence | Notice |
| --- | --- | --- |
| `scriptconv_copyleft/phonemizers/_vendored/kog2p/` | GPL-3.0-only | `LICENSE.md` and `COPYING` in that directory. KoG2P (scarletcho/KoG2P) ships the GPL version 3 text and gives no "or later" grant. |
| `scriptconv_copyleft/phonemizers/lt.py`, `scriptconv_copyleft/phonemizers/_vendored/reginute/lt_raides.tsv`, `scriptconv_copyleft/phonemizers/_vendored/reginute/lt_kreipiniai.tsv` | GPL-3.0-only | Ported or copied from Reginutė (RobertasTa/reginute), whose code is GPL-3.0-only. `COPYING` and `SOURCE` in `_vendored/reginute/`. |
| `scriptconv_copyleft/phonemizers/_vendored/reginute/lt_kirciai.tsv` | CC-BY-4.0 AND GPL-3.0-only | `LICENSE`, `COPYING` and `SOURCE` in that directory. |
| `scriptconv_copyleft/phonemizers/he.py`, `scriptconv_copyleft/phonemizers/ja_prosody.py`, `scriptconv_copyleft/phonemizers/th.py` | GPL-3.0-or-later | Ported from OHF-Voice/piper1-gpl. The GPL text is `_vendored/reginute/COPYING`. |

The entries of the Lithuanian stress dictionary come from the LIEPA corpus
annotation (Vilnius University) and the g2p-lt-lexicon of Arunas Smaliukas,
both CC-BY-4.0. The manual corrections of Reginutė are GPL-3.0-only. The wheel
carries the licence files that `license-files` in `pyproject.toml` names.

---

[Index](index.md) · Previous: [Backend reference](backends.md) · Next: [Index](index.md)

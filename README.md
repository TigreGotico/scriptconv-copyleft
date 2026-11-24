# scriptconv-copyleft

<!-- agent-hint
covers: what scriptconv-copyleft is, the quickstart, the backends it holds and its licence
source: pyproject.toml, scriptconv_copyleft/phonemizers/, scriptconv/phonemizers/registry.py in scriptconv
generated: no
verify: python -m doctest README.md
see: docs/index.md, docs/getting-started.md, AGENTS.md
-->

scriptconv-copyleft holds the phonemizer backends of
[scriptconv](https://github.com/TigreGotico/scriptconv) that have a copyleft
licence (GPL, LGPL or AGPL) in their code or in their dependencies. scriptconv
keeps the registry, and its extras install this package, so you call the
backends through scriptconv as usual.

## Quickstart

```bash
uv pip install --prerelease=allow "scriptconv[espeak]"
```

```python
>>> from scriptconv.phonemizers import Phonemizer, get_phonemizer
>>> get_phonemizer(Phonemizer.ESPEAK).phonemize_string("olá mundo", "pt")
'ɔlˈa mˈũŋdʊ'

```

The backend runs the espeak-ng program when it is on `PATH`, and espyak, its
Python port, when it is not. [Getting started](docs/getting-started.md) walks
through the install, the alphabets and the engine identity.

## Backends

| `Phonemizer` values | scriptconv extra |
| --- | --- |
| `espeak`, `espeak_lt_accent` | `espeak` |
| `transphone` | `transphone` |
| `misaki`, `misaki_en`, `misaki_ja`, `misaki_zh`, `misaki_ko`, `misaki_vi` | `misaki` |
| `cotovia` | `gl` |
| `ahotts` | `eu` |
| `hebrew_ipa` | `he` |
| `tltk` | `th` |
| `g2pfa` | `fa` |
| `pykakasi`, `openjtalk_prosody` | `ja-phonemizers` |
| `g2pk`, `kog2p` | `ko` |

The package also holds the Japanese kanji-to-kana readings that
`scriptconv.readings` gives, through the `ja` extra. The
[backend reference](docs/backends.md) gives the languages, alphabets,
parameters, licence and downloads of each backend.

## Licence

The package is `Apache-2.0 AND GPL-3.0-only AND GPL-3.0-or-later AND CC-BY-4.0`.
Its own glue code is Apache-2.0. The vendored KoG2P code and the code and data
from Reginutė are GPL-3.0-only, and the modules ported from Piper are
GPL-3.0-or-later. The other backends are here because of a dependency, for
example espyak, pycotovia or pykakasi under the GPL. A program that installs
and uses a backend must follow the licences of that backend and of its
dependencies. [Licences](docs/licences.md) gives the copyleft item of each
backend and the licence of each file.

## Documentation

The [documentation index](docs/index.md) lists every page in reading order.
The [scriptconv documentation](https://github.com/TigreGotico/scriptconv/tree/dev/docs)
explains the phonemizer contract and the other backends.

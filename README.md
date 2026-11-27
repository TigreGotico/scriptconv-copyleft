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

The package holds the `espeak`, `transphone`, `misaki`, `cotovia`, `ahotts`,
`hebrew_ipa`, `tltk`, `g2pfa`, `pykakasi`, `openjtalk_prosody`, `g2pk` and
`kog2p` backends, and the Japanese kanji-to-kana readings.

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

| Page | Read it for |
| --- | --- |
| [docs/getting-started.md](docs/getting-started.md) | install, the alphabets, the engine identity |
| [docs/how-it-works.md](docs/how-it-works.md) | how scriptconv finds and imports these backends |
| [docs/backends.md](docs/backends.md) | the extra, languages, alphabets and parameters of each backend |
| [docs/licences.md](docs/licences.md) | the copyleft item of each backend, the licence of each file |
| [docs/index.md](docs/index.md) | every page in reading order |

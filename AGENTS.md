# AGENTS.md

scriptconv-copyleft holds the scriptconv phonemizer backends that have a
copyleft licence in their code or their dependencies. scriptconv keeps the
`Phonemizer` values and the registry; this package holds the classes that the
registry imports on first use.

## Map

| Path | Holds |
|---|---|
| `scriptconv_copyleft/phonemizers/mul.py` | espeak, misaki and transphone |
| `scriptconv_copyleft/phonemizers/lt.py` | `espeak_lt_accent`, ported from Reginutė (GPL-3.0-only) |
| `scriptconv_copyleft/phonemizers/he.py`, `ja_prosody.py`, `th.py` | `hebrew_ipa`, `openjtalk_prosody`, `tltk`, ported from Piper (GPL-3.0-or-later) |
| `scriptconv_copyleft/phonemizers/gl.py`, `eu.py`, `fa.py`, `ja.py`, `ko.py` | Cotovía, AhoTTS, g2pfa, pykakasi, g2pk and KoG2P |
| `scriptconv_copyleft/phonemizers/_vendored/` | KoG2P and the Reginutė data, each with its licence notice |
| `scriptconv_copyleft/readings.py` | The Japanese kanji-to-kana readings |
| `tests/data/` | The Piper parity references |
| `docs/` | The documentation. [docs/index.md](docs/index.md) gives the reading order |

## Setup and tests

```bash
uv venv -p 3.12
uv pip install --prerelease=allow -e '.[test]'
pytest tests/
```

CI runs the suite on Python 3.11, 3.12 and 3.13 with the `espeak-ng` program
installed (`.github/workflows/build-tests.yml`). The misaki tests skip on
Python 3.13, because misaki declares `Requires-Python <3.13`.

## Rules that the code, the tests or the docs enforce

- scriptconv names each class by its module path and class name in
  `PHONEMIZER_REGISTRY`. Renaming or moving a class breaks scriptconv. See
  [docs/how-it-works.md](docs/how-it-works.md).
- `tests/conftest.py` points the scriptconv registry at the classes of this
  checkout. Keep its `MOVED` rows equal to the rows of scriptconv.
- Importing the package imports no backend. Each wrapper imports its engine
  on first use, and a missing engine raises an `ImportError` with an install
  command (`tests/test_phonemizers_friendly_import_errors.py`).
- `hebrew_ipa`, `openjtalk_prosody`, `tltk` and `espeak_lt_accent` give the
  output of the Piper code they port. The references in `tests/data/` and
  their tests check it.
- The `transphone` extra installs every package that transphone would install
  with pip during a call (`tests/test_transphone_extra_declares_auto_installs.py`).
- Each ported or vendored file names its source, commit and licence, and
  `license-files` in `pyproject.toml` lists each licence notice. See
  [docs/licences.md](docs/licences.md).
- The examples of each docs page give the output that the page shows. Run
  the `verify` command in the agent hint of the page.

## Before a push

```bash
pytest tests/
for page in README.md docs/*.md; do python -m doctest "$page" || echo "FAIL $page"; done
```

Run each page in its own process: the first example of
`docs/how-it-works.md` checks that nothing imported this package before it.
The `test` extra installs what the examples need. CI also runs ruff, which
reports only, and actionlint, which fails the job on a broken workflow file.

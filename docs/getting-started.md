# Getting started

<!-- agent-hint
covers: install a copyleft backend through its scriptconv extra, phonemize a text, see which engine ran, and import a class directly
source: pyproject.toml, scriptconv_copyleft/phonemizers/mul.py:EspeakPhonemizer, scriptconv_copyleft/phonemizers/gl.py:CotoviaPhonemizer
generated: no
verify: python -m doctest docs/getting-started.md
see: docs/how-it-works.md, docs/backends.md
-->

This page installs two backends of scriptconv-copyleft, phonemizes text with
each one, and shows which engine gave the phonemes. Each step shows the real
output.

## 1. Install a backend

Install scriptconv with the extra of the backend. The extra installs
scriptconv-copyleft and the dependencies of that backend:

```bash
uv pip install --prerelease=allow "scriptconv[espeak,gl]"
```

The `espeak` extra installs espyak, a Python port of espeak-ng. When the
espeak-ng program is on `PATH`, the backend runs the program. Otherwise it runs
espyak. The `gl` extra installs pycotovia, a Python port of the Cotovía engine
for Galician.

## 2. Phonemize a text

Ask the scriptconv registry for a backend by its `Phonemizer` value. Then give
the text and its language:

```python
>>> from scriptconv.phonemizers import Phonemizer, get_phonemizer
>>> espeak = get_phonemizer(Phonemizer.ESPEAK)
>>> espeak.phonemize_string("olá mundo", "pt")
'ɔlˈa mˈũŋdʊ'

```

The class comes from this package, but you never import it yourself:

```python
>>> type(espeak).__module__
'scriptconv_copyleft.phonemizers.mul'

```

## 3. See which engine ran

`identity(lang)` names the engine and its version. With
`prefer_espyak=True`, the backend runs espyak even when the espeak-ng program
is on `PATH`:

```python
>>> from scriptconv.phonemizers import Phonemizer, get_phonemizer
>>> port = get_phonemizer(Phonemizer.ESPEAK, prefer_espyak=True)
>>> port.phonemize_string("olá mundo", "pt")
'ɔlˈa mˈũŋdʊ'
>>> port.identity("pt").distribution
'espyak'

```

Without `prefer_espyak`, `identity("pt").distribution` is `'espeak-ng'` when
the program is on `PATH`.

## 4. Choose the alphabet and the model

`get_phonemizer` gives `alphabet=` and `model=` to the constructor of the
backend. Cotovía writes its own phoneme notation, or IPA. Its `model="stress"`
marks each stressed vowel with `^`:

```python
>>> from scriptconv.phonemizers import Alphabet, Phonemizer, get_phonemizer
>>> get_phonemizer(Phonemizer.COTOVIA, alphabet=Alphabet.COTOVIA).phonemize_string("Ola mundo", "gl")
'ola mundo '
>>> get_phonemizer(Phonemizer.COTOVIA, model="stress").phonemize_string("Ola mundo", "gl")
'o^la mu^ndo '

```

The [backend reference](backends.md) gives the alphabets and the parameters
of each backend.

## 5. Import a class directly

Each class is also importable from this package:

```python
>>> from scriptconv_copyleft.phonemizers.gl import CotoviaPhonemizer
>>> CotoviaPhonemizer().phonemize_string("Ola mundo", "gl")
'ola mundo '

```

## 6. A backend that is not installed

When the package of a backend is missing, `get_phonemizer` raises an
`ImportError` that names the scriptconv extra to install. This output comes
from a venv with scriptconv only:

```python
from scriptconv.phonemizers import Phonemizer, get_phonemizer

get_phonemizer(Phonemizer.ESPEAK)
# ImportError: phonemizer 'espeak' needs a missing backing package — install with `pip install scriptconv[espeak]`
```

## Next

[How it works](how-it-works.md) shows how scriptconv finds the classes of this
package. The [backend reference](backends.md) lists every backend, its extra
and its downloads.

---
[Home](index.md) · [Next →](how-it-works.md)

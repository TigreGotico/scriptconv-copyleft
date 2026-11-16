"""misaki's Japanese wrapper never calls OpenJTalk.

``misaki.ja`` imports the ``pyopenjtalk`` module, which pyopenjtalk and
pyopenjtalk-plus both install. The wrapper builds ``JAG2P()`` with its default
cutlet reader (fugashi and unidic-lite), which does not call ``pyopenjtalk``. So
the OpenJTalk distribution does not change misaki's phonemes, and the wrapper
needs no check of it. If a misaki release starts to call OpenJTalk here, these
tests fail.

The expected phonemes are misaki 0.9.4's output on pyopenjtalk 0.4.1 and on
pyopenjtalk-plus 0.4.1.post10, which are equal for 1033 of 1033 sentences. The
two sentences are FLORES-200 devtest rows 93 and 95 (CC-BY-SA-4.0), where the
two OpenJTalk distributions read 白煙 and 日本 differently.
"""
import sys
import unittest
from unittest import mock

ROWS = [
    ("テレビの報道によると、原発から白煙が上がっています。",
     "teɾebʲi no hoːdoː ɲi joɾɯ to, ɡempaʦɨ kaɾa hakɯeɴ ɡa aɡaʔte imasɨ."),
    ("日本の原子力庁によれば、原発内で放射性セシウムとヨウ素が特定されています。",
     "ɲiʔpoɴ no ɡeɴɕiɾʲokɯ ʨoː ɲi joɾeba, ɡempaʦɨ nai de hoːɕa seː seɕiɯmɯ to joːso ɡa tokɯteː saɾete imasɨ."),
]

OPENJTALK_CALLS = ("run_frontend", "g2p", "extract_fullcontext", "make_label")


@unittest.skipIf(sys.version_info >= (3, 13), "misaki declares Requires-Python <3.13")
class TestMisakiJapaneseReader(unittest.TestCase):
    def test_the_reader_never_calls_openjtalk(self):
        import pyopenjtalk

        from scriptconv_copyleft.phonemizers.mul import (
            MisakiJaPhonemizer,
            MisakiPhonemizer,
        )

        def refuse(*args, **kwargs):
            raise AssertionError("misaki's Japanese wrapper called OpenJTalk")

        with mock.patch.multiple(pyopenjtalk, **{name: refuse for name in OPENJTALK_CALLS}):
            for phonemizer, lang in ((MisakiJaPhonemizer(), "ja"), (MisakiPhonemizer(), "ja-JP")):
                for text, expected in ROWS:
                    with self.subTest(phonemizer=type(phonemizer).__name__, text=text):
                        self.assertEqual(phonemizer.phonemize_string(text, lang), expected)

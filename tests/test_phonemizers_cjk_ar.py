import sys
import unicodedata
import unittest

from scriptconv.phonemizers import Phonemizer, get_phonemizer_class
from scriptconv.phonemizers.enums import Alphabet
from scriptconv.phonemizers.registry import get_phonemizer


class TestG2PKOnPython313(unittest.TestCase):
    """scriptconv[ko] installs g2pk only below Python 3.13, because
    python-mecab-ko has wheels up to CPython 3.12 only. On 3.13 and later,
    pip builds python-mecab-ko from its sdist, which needs mecab-config
    from an installed MeCab-ko."""

    def _message(self, version_info):
        from unittest.mock import patch
        from scriptconv_copyleft.phonemizers.ko import G2PKPhonemizer
        with patch.dict(sys.modules, {"g2pk": None}), \
                patch.object(sys, "version_info", version_info):
            with self.assertRaises(ImportError) as ctx:
                G2PKPhonemizer()
        return str(ctx.exception)

    def test_313_says_to_install_mecab_ko_first_not_the_extra(self):
        message = self._message((3, 13, 0, "final", 0))
        self.assertIn("mecab-config", message)
        self.assertIn("'pip install g2pk'", message)
        self.assertNotIn("Python 3.12 or older", message)
        self.assertNotIn("scriptconv[ko]", message)

    def test_312_names_the_extra(self):
        self.assertIn("scriptconv[ko]", self._message((3, 12, 0, "final", 0)))


class TestMisakiKoreanAlphabet(unittest.TestCase):
    """misaki's KOG2P writes the pronunciation in Hangul, not IPA.

    Wikipedia, "Korean phonology", revision 1374882945, section "Consonant
    assimilation": a velar stop becomes [ŋ] before a nasal stop, and
    한국말 is pronounced 한궁말. KOG2P writes conjoining jamo, which is the
    NFD form of the Hangul syllables.
    """

    def test_ipa_is_refused(self):
        with self.assertRaises(ValueError):
            get_phonemizer(Phonemizer.MISAKI_KO, Alphabet.IPA)

    @unittest.skipIf(sys.version_info >= (3, 13), "misaki declares Requires-Python <3.13")
    def test_output_is_the_pronunciation_in_hangul(self):
        from scriptconv_copyleft.phonemizers.mul import MisakiKoPhonemizer
        p = MisakiKoPhonemizer()
        self.assertEqual(p.alphabet, Alphabet.HANGUL)
        self.assertEqual(p.phonemize_string("한국말", "ko"),
                         unicodedata.normalize("NFD", "한궁말"))


class TestLicensingStubs(unittest.TestCase):
    def test_kog2p_wrapper_constructs_from_vendored_copy(self):
        cls = get_phonemizer_class(Phonemizer.KOG2PK)
        p = cls()
        self.assertTrue(callable(p.g2p))

    def test_quarantine_carries_license_notices(self):
        import pathlib
        base = pathlib.Path("scriptconv_copyleft/phonemizers/_vendored")
        self.assertTrue((base / "kog2p" / "LICENSE.md").is_file())
        self.assertTrue((base / "kog2p" / "COPYING").is_file())

    def test_quarantine_not_imported_at_package_import(self):
        import subprocess, sys
        code = ("import sys, scriptconv_copyleft, scriptconv_copyleft.phonemizers; "
                "bad=[m for m in sys.modules if '_vendored' in m]; "
                "print(bad); sys.exit(1 if bad else 0)")
        proc = subprocess.run([sys.executable, "-c", code],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout)


class TestUnsupportedAlphabetIsAClearError(unittest.TestCase):
    """A wrapper asked for an alphabet it cannot emit must say so.

    ``get_phonemizer`` injects its own ``alphabet=`` default (IPA) into every
    constructor declaring the parameter, so the Japanese wrappers — which emit
    romanizations, never IPA — were hit by ordinary registry use and raised a
    bare ``AssertionError`` with an empty message.
    """

    def test_registry_default_raises_valueerror_naming_the_alphabets(self):
        from scriptconv.phonemizers.enums import Alphabet
        for member in (Phonemizer.PYKAKASI,):
            with self.subTest(phonemizer=member.value):
                try:
                    get_phonemizer(member)
                except ImportError:
                    self.skipTest(f"{member.value} backend not installed")
                except ValueError as e:
                    self.assertIn("ipa", str(e))
                    self.assertIn(Alphabet.HEPBURN.value, str(e))
                else:
                    self.fail("expected ValueError for an unemittable alphabet")


if __name__ == "__main__":
    unittest.main()

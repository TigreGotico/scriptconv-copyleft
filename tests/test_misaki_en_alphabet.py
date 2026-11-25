"""misaki English accepts the misaki alphabet and IPA, and refuses the others.

``Alphabet.MISAKI`` names the misaki codes (scriptconv ``docs/notation.md``,
"Misaki → IPA"). Building the phonemizer loads no misaki module, so these tests
need no misaki install.
"""
import unittest

from scriptconv.phonemizers.enums import Alphabet

from scriptconv_copyleft.phonemizers.mul import MisakiEnPhonemizer


class TestMisakiEnAlphabet(unittest.TestCase):
    def test_the_misaki_alphabet_is_accepted(self):
        self.assertEqual(MisakiEnPhonemizer(Alphabet.MISAKI).alphabet, Alphabet.MISAKI)

    def test_ipa_stays_the_default(self):
        self.assertEqual(MisakiEnPhonemizer().alphabet, Alphabet.IPA)

    def test_an_alphabet_misaki_cannot_write_raises(self):
        for alphabet in (Alphabet.ARPA, Alphabet.XSAMPA, Alphabet.BOPOMOFO):
            with self.subTest(alphabet=alphabet), self.assertRaises(ValueError):
                MisakiEnPhonemizer(alphabet)


if __name__ == "__main__":
    unittest.main()

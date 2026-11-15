"""A deprecated language code and its Preferred-Value name one language.

RFC 5646 section 4.5 replaces a deprecated subtag by its Preferred-Value, so
``ajp`` and ``apc`` measure the same distance to a request, and so do ``yol``
and ``enm`` (IANA Language Subtag Registry). When a supported list holds both
codes, the code the request spells wins the tie, whatever the list order.
"""
import unittest

from scriptconv_copyleft.phonemizers.mul import TransphonePhonemizer


class TestPreferredValueTie(unittest.TestCase):
    def test_transphone_language_list(self):
        self.assertIn("ajp", TransphonePhonemizer.TRANSPHONE_LANGS)
        self.assertIn("enm", TransphonePhonemizer.TRANSPHONE_LANGS)
        self.assertEqual(TransphonePhonemizer.get_lang("apc-SY"), "apc")
        self.assertEqual(TransphonePhonemizer.get_lang("yol-IE"), "yol")


if __name__ == "__main__":
    unittest.main()

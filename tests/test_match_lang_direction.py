"""Language matching measures the requested tag against each supported tag.

``linguatag.lang_distance(desired, supported)`` is not symmetric: an Arabic
variety such as ``arz`` is near Modern Standard Arabic, but ``ar`` is not near
``arz``. Each expected value here comes from linguatag itself, called with the
requested tag first.
"""
import unittest

from linguatag import closest_lang

from scriptconv_copyleft.phonemizers.mul import EspeakPhonemizer

ARABIC_VARIETIES = ["arz", "arz-EG", "apc", "apc-SY", "ajp", "acm", "acm-IQ", "afb",
                    "aeb", "ary", "ary-MA", "arq", "ars", "acw"]


class TestArabicVarietyPhonemizers(unittest.TestCase):
    def assert_matches_linguatag(self, phonemizer, pool):
        for tag in ARABIC_VARIETIES:
            expected = closest_lang(tag, pool)
            self.assertIsNotNone(expected)
            with self.subTest(phonemizer=phonemizer.__name__, tag=tag):
                self.assertEqual(phonemizer.get_lang(tag), expected)

    def test_espeak(self):
        self.assert_matches_linguatag(EspeakPhonemizer, EspeakPhonemizer.ESPEAK_LANGS)


if __name__ == "__main__":
    unittest.main()

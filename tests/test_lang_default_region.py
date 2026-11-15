"""Language matching follows the default-region rule.

A bare tag means the region where the language first appeared and is still
spoken: ``en`` is British English and ``pt`` is European Portuguese.
"""
import unittest

from scriptconv_copyleft.phonemizers.mul import (EspeakPhonemizer, MisakiEnPhonemizer,
                                                 TransphonePhonemizer)


class TestPhonemizerDefaultRegion(unittest.TestCase):
    def test_misaki_bare_en_is_british(self):
        self.assertEqual(MisakiEnPhonemizer.get_lang("en"), "en-GB")

    def test_espeak_bare_en_is_british(self):
        self.assertEqual(EspeakPhonemizer.get_lang("en"), "en-gb")


class TestHongKongCantonese(unittest.TestCase):
    """Hong Kong and Macau tags reach each backend's Cantonese entry.

    A bare ``yue`` is mainland Cantonese in Simplified script, so these tags
    are far from it by language distance.
    """
    TAGS = ["yue-HK", "yue-Hant", "yue-MO", "yue-Hant-HK", "zh-HK", "zh-MO",
            "zh-Hant-HK", "zh-Hant-MO", "yue_HK", "ZH-hk"]

    def test_transphone(self):
        self.assertIn("yue", TransphonePhonemizer.TRANSPHONE_LANGS)
        for tag in self.TAGS:
            with self.subTest(tag=tag):
                self.assertEqual(TransphonePhonemizer.get_lang(tag), "yue")

    def test_espeak(self):
        self.assertIn("yue", EspeakPhonemizer.ESPEAK_LANGS)
        for tag in ["zh-HK", "zh-MO", "zh-Hant-HK", "zh-Hant-MO", "yue-HK"]:
            with self.subTest(tag=tag):
                self.assertEqual(EspeakPhonemizer.get_lang(tag), "yue")

    def test_taiwan_stays_mandarin(self):
        for tag in ["zh-TW", "zh-Hant", "zh-Hant-TW"]:
            with self.subTest(tag=tag):
                self.assertEqual(EspeakPhonemizer.get_lang(tag), "cmn")


if __name__ == "__main__":
    unittest.main()

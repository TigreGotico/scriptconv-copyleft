import unittest

from scriptconv.phonemizers import Alphabet, Phonemizer, get_phonemizer, phonemizer_for_lang


class TestLangDefaults(unittest.TestCase):
    def test_cotovia_only_for_cotovia_alphabet(self):
        # requesting IPA must never yield Cotovía (it emits its own notation);
        # the in-house chain falls through to orthography2ipa (or espeak)
        gl_ipa = phonemizer_for_lang("gl", alphabet=Alphabet.IPA)
        self.assertIn(type(gl_ipa).__name__,
                      ("Orthography2IPAPhonemizer", "EspeakPhonemizer"))
        self.assertNotEqual(type(gl_ipa).__name__, "CotoviaPhonemizer")
        gl_ctv = phonemizer_for_lang("gl", alphabet=Alphabet.COTOVIA)
        self.assertEqual(type(gl_ctv).__name__, "CotoviaPhonemizer")

    def test_fallback_prefers_o2i_then_espeak(self):
        # in-house first: orthography2ipa is the usual default when it has a
        # spec for the language; espeak only as last resort
        from unittest import mock
        import scriptconv.phonemizers.registry as reg
        with mock.patch.object(reg, "_o2i_supports", return_value=True):
            with mock.patch.object(reg, "get_phonemizer") as gp:
                reg.phonemizer_for_lang("de-DE")
                self.assertEqual(gp.call_args[0][0], Phonemizer.ORTHOGRAPHY2IPA)
        with mock.patch.object(reg, "_o2i_supports", return_value=False):
            de = reg.phonemizer_for_lang("de-DE")
            self.assertEqual(type(de).__name__, "EspeakPhonemizer")

    def test_normalizer_set_on_wrapper_with_custom_init(self):
        # EspeakPhonemizer.__init__ does not accept normalizer= — the factory
        # sets the attribute after construction
        norm = lambda t, l: t
        e = get_phonemizer(Phonemizer.ESPEAK, normalizer=norm)
        self.assertIs(e.normalizer, norm)


class TestEspeakGetLangChinese(unittest.TestCase):
    """espeak-ng ships no bare "zh"/region-tagged Chinese voice, only "cmn"
    and "yue" — get_lang must map BCP-47 Chinese tags onto those directly."""

    def _get_lang(self):
        from scriptconv_copyleft.phonemizers.mul import EspeakPhonemizer
        return EspeakPhonemizer.get_lang

    def test_zh_region_tags_resolve_to_supported_voice(self):
        from scriptconv_copyleft.phonemizers.mul import EspeakPhonemizer
        get_lang = self._get_lang()
        for code in ("zh", "zh-CN", "zh-TW", "zh-HK", "zh-Hant-TW"):
            resolved = get_lang(code)
            self.assertIn(resolved, EspeakPhonemizer.ESPEAK_LANGS,
                           f"{code} -> {resolved}")

    def test_en_gb_special_case_unchanged(self):
        get_lang = self._get_lang()
        self.assertEqual(get_lang("en-gb"), "en-gb-x-rp")

    def test_unsupported_code_still_raises(self):
        get_lang = self._get_lang()
        with self.assertRaises(ValueError):
            get_lang("xx-not-a-real-lang")


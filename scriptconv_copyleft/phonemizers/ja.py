from scriptconv.phonemizers.base import BasePhonemizer, _check_alphabet
from scriptconv.phonemizers.enums import Alphabet


class PyKakasiPhonemizer(BasePhonemizer):
    engine_distribution = "pykakasi"

    def __init__(self, alphabet=Alphabet.HEPBURN):
        _check_alphabet(self, alphabet,
                        [Alphabet.HEPBURN, Alphabet.KANA, Alphabet.HIRA])
        # kana, hira, hepburn
        try:
            import pykakasi
        except ImportError as e:
            raise ImportError(
                "pykakasi is required for the PyKakasi phonemizer. "
                "Install it with 'pip install pykakasi' "
                "(or 'pip install scriptconv[ja-phonemizers]')."
            ) from e
        self.g2p = pykakasi.kakasi()
        super().__init__(alphabet)

    @classmethod
    def get_lang(cls, target_lang: str) -> str:
        """
        Validates and returns the closest supported language code.

        Args:
            target_lang (str): The language code to validate.

        Returns:
            str: The validated language code.

        Raises:
            ValueError: If the language code is unsupported.
        """
        # this check is here only to throw an exception if invalid language is provided
        return cls.match_lang(target_lang, ["ja"])

    def phonemize_string(self, text: str, lang: str = "ja") -> str:
        """
        """
        lang = self.get_lang(lang)
        return " ".join([
            a[self.alphabet] for a in
            self.g2p.convert(text)
        ])

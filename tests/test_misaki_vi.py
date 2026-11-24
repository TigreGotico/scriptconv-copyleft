"""The ``misaki`` extra installs what misaki's Vietnamese G2P imports.

misaki 0.9.4 ``misaki/vi.py`` imports underthesea, which the ``vi`` extra of
misaki declares, and ``misaki/vi_cleaner/datestime_vi.py`` imports
vietnam_number, which misaki does not declare.

misaki declares ``Requires-Python <3.13``, so the ``test`` extra installs it
only below 3.13 and this test runs only there.
"""
import sys
import unittest

from scriptconv.phonemizers import Phonemizer
from scriptconv.phonemizers.registry import get_phonemizer


@unittest.skipIf(sys.version_info >= (3, 13), "misaki declares Requires-Python <3.13")
class TestMisakiVietnamese(unittest.TestCase):
    def test_misaki_vi_gives_the_phonemes_of_misaki(self):
        from misaki.vi import VIG2P
        expected, _ = VIG2P()("xin chào")
        self.assertEqual(get_phonemizer(Phonemizer.MISAKI_VI).phonemize_string("xin chào", "vi"), expected)


if __name__ == "__main__":
    unittest.main()

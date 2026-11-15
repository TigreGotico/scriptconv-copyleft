"""Pins the friendly-ImportError convention for the lazy backend imports
inside the phonemizer wrappers this package holds.

Each wrapper imports its backend lazily, inside ``__init__`` or a method.
This test forces that lazy import to fail (by shadowing the backend module
in ``sys.modules`` with ``None``) and asserts the resulting exception is an
``ImportError`` whose message contains an install instruction.
"""
import sys
import unittest
from unittest.mock import patch

from scriptconv.phonemizers import Phonemizer, get_phonemizer_class


def _trigger_construct(cls):
    cls()


def _trigger_misaki_en(cls):
    p = cls()
    p._get_phonemizer("en-US")


# member -> (module name to blank out in sys.modules, how to trigger the
# lazy import that consumes it)
CASES = {
    Phonemizer.MISAKI: ("misaki", _trigger_misaki_en),
    Phonemizer.MISAKI_EN: ("misaki", _trigger_misaki_en),
    Phonemizer.TRANSPHONE: ("transphone", _trigger_construct),
    Phonemizer.PYKAKASI: ("pykakasi", _trigger_construct),
    Phonemizer.G2PK: ("g2pk", _trigger_construct),
}


class TestLazyBackendImportsAreFriendly(unittest.TestCase):
    def _assert_friendly(self, member):
        module_name, trigger = CASES[member]
        cls = get_phonemizer_class(member)
        self.assertTrue(cls.__module__.startswith("scriptconv_copyleft."), cls.__module__)
        with patch.dict(sys.modules, {module_name: None}):
            with self.assertRaises(ImportError, msg=member) as ctx:
                trigger(cls)
        msg = str(ctx.exception)
        self.assertIn("pip install", msg, member)

    def test_misaki(self):
        self._assert_friendly(Phonemizer.MISAKI)

    def test_misaki_en(self):
        self._assert_friendly(Phonemizer.MISAKI_EN)

    def test_transphone(self):
        self._assert_friendly(Phonemizer.TRANSPHONE)

    def test_pykakasi(self):
        self._assert_friendly(Phonemizer.PYKAKASI)

    def test_g2pk(self):
        # Below Python 3.13 the message names scriptconv[ko]. The 3.13
        # message is checked in test_phonemizers_cjk_ar.py.
        with patch("sys.version_info", (3, 12, 9)):
            self._assert_friendly(Phonemizer.G2PK)


if __name__ == "__main__":
    unittest.main()

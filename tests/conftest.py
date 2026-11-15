"""Point the scriptconv registry at the classes this package holds."""

from unittest import mock

import pytest

from scriptconv.phonemizers.enums import Phonemizer as _P
from scriptconv.phonemizers.registry import PHONEMIZER_REGISTRY

_BASE = "scriptconv_copyleft.phonemizers"

MOVED = {
    _P.ESPEAK: (f"{_BASE}.mul", "EspeakPhonemizer", "espeak"),
    _P.TRANSPHONE: (f"{_BASE}.mul", "TransphonePhonemizer", "transphone"),
    _P.MISAKI: (f"{_BASE}.mul", "MisakiPhonemizer", "misaki"),
    _P.MISAKI_EN: (f"{_BASE}.mul", "MisakiEnPhonemizer", "misaki"),
    _P.MISAKI_JA: (f"{_BASE}.mul", "MisakiJaPhonemizer", "misaki"),
    _P.MISAKI_ZH: (f"{_BASE}.mul", "MisakiZhPhonemizer", "misaki"),
    _P.MISAKI_KO: (f"{_BASE}.mul", "MisakiKoPhonemizer", "misaki"),
    _P.MISAKI_VI: (f"{_BASE}.mul", "MisakiViPhonemizer", "misaki"),
    _P.COTOVIA: (f"{_BASE}.gl", "CotoviaPhonemizer", "gl"),
    _P.AHOTTS: (f"{_BASE}.eu", "AhoTTSPhonemizer", "eu"),
    _P.G2PFA: (f"{_BASE}.fa", "PersianPhonemizer", "fa"),
    _P.PYKAKASI: (f"{_BASE}.ja", "PyKakasiPhonemizer", "ja-phonemizers"),
    _P.G2PK: (f"{_BASE}.ko", "G2PKPhonemizer", "ko"),
    _P.KOG2PK: (f"{_BASE}.ko", "KoG2PPhonemizer", "ko"),
}


@pytest.fixture(autouse=True, scope="session")
def _registry_points_here():
    with mock.patch.dict(PHONEMIZER_REGISTRY, MOVED):
        yield

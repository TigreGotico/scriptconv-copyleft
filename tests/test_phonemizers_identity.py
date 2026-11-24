"""``PhonemizerIdentity`` for the wrappers this package holds."""
import re
import sys
from importlib import metadata
from unittest import mock

import espyak.version
import pytest
from scriptconv.phonemizers._revision import FORMAT as REVISION_FORMAT

from scriptconv_copyleft.phonemizers.ko import G2PKPhonemizer
from scriptconv_copyleft.phonemizers.mul import EspeakPhonemizer


class TestIdentity:
    # g2pk needs python-mecab-ko, which has no Python 3.13 wheel and needs
    # mecab-config to build, so the test extra installs g2pk below 3.13 only.
    @pytest.mark.skipif(sys.version_info >= (3, 13),
                        reason="python-mecab-ko has no Python 3.13 wheel")
    def test_g2pk_reports_the_installed_engine(self):
        identity = G2PKPhonemizer().identity("ko")
        assert (identity.backend, identity.distribution, identity.version, identity.lang, identity.frontend) == \
            ("g2pk", "g2pk", metadata.version("g2pk"), "ko", None)
        # the revision of an in-tree backend is the hash of the code on its path
        assert re.fullmatch(rf"{REVISION_FORMAT}:[0-9a-f]{{64}}", identity.revision)

    @pytest.mark.skipif(sys.version_info >= (3, 13),
                        reason="python-mecab-ko has no Python 3.13 wheel")
    def test_a_g2pk_release_changes_the_revision(self):
        with mock.patch.object(G2PKPhonemizer, "_engine_release", return_value=("g2pk", "0.0.0")):
            other = G2PKPhonemizer().identity("ko")
        assert other.revision != G2PKPhonemizer().identity("ko").revision

    def test_espeak_reports_the_binary_version(self):
        banner = "eSpeak NG text-to-speech: 1.52.0  Data at: /usr/share/espeak-ng-data\n"
        with mock.patch.object(EspeakPhonemizer, "_has_binary", return_value=True), \
                mock.patch.object(EspeakPhonemizer, "_run_espeak_command", return_value=banner):
            identity = EspeakPhonemizer().identity("pt")
        assert (identity.distribution, identity.version) == ("espeak-ng", "1.52.0")

    def test_espeak_without_the_binary_reports_the_port(self):
        with mock.patch.object(EspeakPhonemizer, "_has_binary", return_value=False):
            identity = EspeakPhonemizer().identity("pt")
        assert (identity.distribution, identity.version) == ("espyak", espyak.version.VERSION_STR)

    def test_a_preferred_port_that_is_missing_reports_the_binary(self):
        banner = "eSpeak NG text-to-speech: 1.52.0  Data at: /usr/share/espeak-ng-data"
        missing = metadata.PackageNotFoundError("espyak")
        with mock.patch.object(EspeakPhonemizer, "_has_binary", return_value=True), \
                mock.patch.object(EspeakPhonemizer, "_run_espeak_command", return_value=banner), \
                mock.patch("scriptconv_copyleft.phonemizers.mul.metadata.version", side_effect=missing):
            identity = EspeakPhonemizer(prefer_espyak=True).identity("pt")
        assert (identity.distribution, identity.version) == ("espeak-ng", "1.52.0")

    def test_the_espyak_port_reports_itself(self):
        identity = EspeakPhonemizer(prefer_espyak=True).identity("pt")
        assert (identity.backend, identity.distribution, identity.version) == \
            ("espeak", "espyak", espyak.version.VERSION_STR)

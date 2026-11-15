"""misaki's Japanese G2P runs only on pyopenjtalk-plus with onnxruntime.

``misaki.ja`` imports the ``pyopenjtalk`` module, which pyopenjtalk and
pyopenjtalk-plus both install. The wrapper checks the owner of the module before
it builds the G2P, and the extras install pyopenjtalk-plus only.
"""
import base64
import hashlib
import sys
from importlib import metadata
from types import SimpleNamespace

import pyopenjtalk
import pytest
from packaging.requirements import Requirement

from scriptconv_copyleft.phonemizers.mul import MisakiJaPhonemizer, MisakiPhonemizer

VERSIONS = {"pyopenjtalk": "0.4.1", "pyopenjtalk-plus": "0.4.1.post10"}
ORDERS = [["pyopenjtalk", "pyopenjtalk-plus"], ["pyopenjtalk-plus", "pyopenjtalk"]]


def _record_hash(content: bytes) -> SimpleNamespace:
    value = base64.urlsafe_b64encode(hashlib.sha256(content).digest()).rstrip(b"=").decode()
    return SimpleNamespace(mode="sha256", value=value)


@pytest.fixture
def both_installed(tmp_path, monkeypatch):
    """pyopenjtalk and pyopenjtalk-plus both record ``pyopenjtalk/__init__.py``.

    The file on disk holds the content of the distribution that the test names
    as the owner, as when that distribution was installed last.
    """
    module_file = tmp_path / "pyopenjtalk" / "__init__.py"
    module_file.parent.mkdir()
    contents = {name: f"# {name}\n".encode() for name in VERSIONS}

    def install(owner: str, order: list[str]):
        module_file.write_bytes(contents[owner])
        dists = {name: SimpleNamespace(files=[SimpleNamespace(hash=_record_hash(contents[name]),
                                                              locate=lambda: module_file)])
                 for name in VERSIONS}
        monkeypatch.setattr(pyopenjtalk, "__file__", str(module_file))
        monkeypatch.setattr(metadata, "packages_distributions", lambda: {"pyopenjtalk": order})
        monkeypatch.setattr(metadata, "distribution", dists.__getitem__)

    return install


@pytest.fixture
def fake_misaki_ja(monkeypatch):
    """A stand-in for ``misaki.ja``, so that the check runs where misaki is not installed."""
    built = []
    monkeypatch.setitem(sys.modules, "misaki.ja", SimpleNamespace(JAG2P=lambda: built.append(1) or "g2p"))
    return built


@pytest.mark.parametrize("owner", VERSIONS)
@pytest.mark.parametrize("order", ORDERS)
def test_module_distribution_names_the_owner(both_installed, owner, order):
    from scriptconv_copyleft.phonemizers.openjtalk_engine import module_distribution

    both_installed(owner, order)
    assert module_distribution("pyopenjtalk", pyopenjtalk.__file__) == owner


@pytest.mark.parametrize("cls", [MisakiJaPhonemizer, MisakiPhonemizer])
@pytest.mark.parametrize("order", ORDERS)
def test_misaki_ja_refuses_the_pyopenjtalk_module(both_installed, fake_misaki_ja, cls, order):
    both_installed("pyopenjtalk", order)
    with pytest.raises(ImportError) as refusal:
        cls()._get_phonemizer("ja")
    assert str(refusal.value) == (
        "misaki's Japanese G2P needs pyopenjtalk-plus, but the installed pyopenjtalk module comes from "
        "pyopenjtalk. Run 'pip uninstall pyopenjtalk', then "
        "'pip install --force-reinstall pyopenjtalk-plus[onnxruntime]', or install "
        "'scriptconv-copyleft[misaki]' in a new environment."
    )
    assert fake_misaki_ja == []


def test_misaki_ja_refuses_a_pyopenjtalk_namespace_package(fake_misaki_ja, monkeypatch):
    """An uninstall of one distribution leaves a namespace package with no ``__file__``."""
    monkeypatch.setattr(pyopenjtalk, "__file__", None)
    with pytest.raises(ImportError, match=r"comes from an unknown distribution\. Run 'pip uninstall pyopenjtalk'"):
        MisakiJaPhonemizer()._get_phonemizer("ja")
    assert fake_misaki_ja == []


def test_misaki_ja_refuses_to_run_without_onnxruntime(fake_misaki_ja, monkeypatch):
    monkeypatch.setitem(sys.modules, "onnxruntime", None)
    with pytest.raises(ImportError, match=r"onnxruntime.*scriptconv-copyleft\[misaki\]"):
        MisakiJaPhonemizer()._get_phonemizer("ja")
    assert fake_misaki_ja == []


@pytest.mark.parametrize("error", ["ImportError", "OSError"])
def test_misaki_ja_refuses_an_onnxruntime_that_does_not_import(fake_misaki_ja, tmp_path, monkeypatch, error):
    """``find_spec`` finds this onnxruntime, but its import raises."""
    package = tmp_path / "onnxruntime"
    package.mkdir()
    (package / "__init__.py").write_text(f"raise {error}('libonnxruntime.so: cannot open shared object file')\n")
    monkeypatch.syspath_prepend(str(tmp_path))
    monkeypatch.delitem(sys.modules, "onnxruntime", raising=False)
    with pytest.raises(ImportError, match=r"needs onnxruntime.*does not import"):
        MisakiJaPhonemizer()._get_phonemizer("ja")
    assert fake_misaki_ja == []


@pytest.mark.parametrize("order", ORDERS)
def test_misaki_ja_runs_on_pyopenjtalk_plus(both_installed, fake_misaki_ja, order):
    both_installed("pyopenjtalk-plus", order)
    assert MisakiJaPhonemizer()._get_phonemizer("ja") == "g2p"
    assert fake_misaki_ja == [1]


def test_no_extra_installs_pyopenjtalk():
    names = [Requirement(r).name for r in metadata.requires("scriptconv-copyleft")]
    assert "pyopenjtalk" not in names


def test_the_misaki_extra_installs_pyopenjtalk_plus_with_onnxruntime():
    requirements = [Requirement(r) for r in metadata.requires("scriptconv-copyleft")]
    plus = [r for r in requirements if r.name == "pyopenjtalk-plus" and r.marker.evaluate({"extra": "misaki", "python_version": "3.12"})]
    assert [(r.extras, str(r.specifier)) for r in plus] == [({"onnxruntime"}, ">=0.4.1.post10")]

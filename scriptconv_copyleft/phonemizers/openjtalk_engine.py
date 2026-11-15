"""The OpenJTalk engine under the Japanese backends: pyopenjtalk-plus with onnxruntime.

Two distributions install the ``pyopenjtalk`` module: pyopenjtalk
(github.com/r9y9/pyopenjtalk) and pyopenjtalk-plus
(github.com/tsukumijima/pyopenjtalk-plus, MIT). Their dictionaries and accent
rules differ, and pyopenjtalk-plus without onnxruntime turns off its model for
the reading of 何. The Japanese backends run only on pyopenjtalk-plus with
onnxruntime, so that one engine stands behind each backend identity.
"""

import base64
import hashlib
from importlib import metadata
from pathlib import Path

ENGINE_DISTRIBUTION = "pyopenjtalk-plus"


def module_distribution(module: str, module_file: str | None) -> str | None:
    """The distribution whose installed files hold *module_file*.

    Two distributions can both list the module's files in their RECORD, when
    both are installed. The one whose recorded sha256 matches the file on disk
    is the one installed last, whose code runs. A module with no file, such as
    the namespace package that an uninstall of one of the two leaves, has no
    owner.
    """
    if module_file is None:
        return None
    path = Path(module_file).resolve()
    digest = base64.urlsafe_b64encode(hashlib.sha256(path.read_bytes()).digest()).rstrip(b"=").decode()
    for name in metadata.packages_distributions().get(module, []):
        for file in metadata.distribution(name).files or ():
            if (file.hash is not None and file.hash.mode == "sha256" and file.hash.value == digest
                    and Path(file.locate()).resolve() == path):
                return name
    return None


def require_pyopenjtalk_plus(backend: str, extra: str) -> None:
    """Raise ImportError unless ``pyopenjtalk`` comes from pyopenjtalk-plus and onnxruntime imports.

    Args:
        backend: The backend name for the message.
        extra: The scriptconv-copyleft extra that installs the engine.
    """
    install = f"Install it with 'pip install scriptconv-copyleft[{extra}]'."
    try:
        import pyopenjtalk
    except ImportError as e:
        raise ImportError(f"{backend} needs pyopenjtalk-plus. {install}") from e
    owner = module_distribution("pyopenjtalk", pyopenjtalk.__file__)
    if owner != ENGINE_DISTRIBUTION:
        raise ImportError(
            f"{backend} needs pyopenjtalk-plus, but the installed pyopenjtalk module comes from "
            f"{owner or 'an unknown distribution'}. Run 'pip uninstall pyopenjtalk', then "
            f"'pip install --force-reinstall pyopenjtalk-plus[onnxruntime]', or install "
            f"'scriptconv-copyleft[{extra}]' in a new environment."
        )
    try:
        import onnxruntime  # noqa: F401
    except Exception as e:
        raise ImportError(
            f"{backend} needs onnxruntime, which pyopenjtalk-plus uses to read 何, and it does not import. "
            f"Run 'pip install --force-reinstall onnxruntime', or install 'scriptconv-copyleft[{extra}]'."
        ) from e

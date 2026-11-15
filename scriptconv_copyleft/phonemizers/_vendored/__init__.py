"""Vendored upstream code under its own licence, stated in its directory.

* ``kog2p/`` — Korean G2P (github.com/scarletcho/KoG2P), **GPL-3.0-only**.
  See ``kog2p/LICENSE.md`` and ``kog2p/COPYING``.

Nothing imports it at package import time; it loads only when a caller
requests :class:`scriptconv_copyleft.phonemizers.ko.KoG2PPhonemizer`.
"""

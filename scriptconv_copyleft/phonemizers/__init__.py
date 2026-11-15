"""Phonemizer wrappers moved out of scriptconv for their copyleft licences.

Each module mirrors the scriptconv module it came from
(``scriptconv.phonemizers.mul``, ``.gl``, ``.eu``, ``.fa``, ``.ko``, ``.ja``).
The classes subclass :class:`scriptconv.phonemizers.base.BasePhonemizer`, and
scriptconv's registry imports them lazily.
"""

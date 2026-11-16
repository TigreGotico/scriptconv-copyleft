"""The committed parity samples, with Piper's output as the reference.

Each file in ``tests/data`` starts with a header line that names the source
and the licence of the sentences and the command that made the expected
values. Each next line holds one ``input`` and the ``expected`` phonemes, a
list of sentences of symbols, from that command.
"""
import json
from pathlib import Path

DATA = Path(__file__).parent / "data"


def parity_rows(backend: str) -> list[tuple[str, list[list[str]]]]:
    lines = (DATA / f"piper_{backend}.jsonl").read_text(encoding="utf-8").splitlines()
    header = json.loads(lines[0])
    assert header["source"] and header["licence"] and header["reference"]
    return [(row["input"], row["expected"]) for row in map(json.loads, lines[1:])]

"""Unicode-safe normalization and a phonetic 'skeleton' for Thanglish matching."""
import re
import unicodedata

_TAMIL = re.compile(r"[஀-௿]")
_SPACE = re.compile(r"\s+")


def normalize(text: str) -> str:
    """NFKC + casefold + trim + collapse whitespace; punctuation (apostrophes) removed."""
    t = unicodedata.normalize("NFKC", text or "").casefold()
    t = re.sub(r"[‘’'`\"]", "", t)
    t = re.sub(r"[^\w\s]", " ", t)
    return _SPACE.sub(" ", t).strip()


def is_tamil(text: str) -> bool:
    return bool(_TAMIL.search(text or ""))


def skeleton(text: str) -> str:
    """Collapse common Tamil-in-Latin spelling variations (thakkali/takkali/takali -> takali)."""
    t = normalize(text)
    if is_tamil(t):
        return t
    t = t.replace("'", "")
    for a, b in (
        ("zh", "l"), ("sh", "s"), ("ch", "s"), ("th", "t"), ("dh", "t"), ("kh", "k"), ("gh", "k"),
        ("bh", "b"), ("ph", "p"), ("ee", "i"), ("oo", "u"), ("aa", "a"), ("ai", "e"), ("ay", "e"),
        ("ou", "u"), ("w", "v"), ("z", "s"), ("c", "k"), ("q", "k"), ("y", "i"), ("d", "t"), ("g", "k"),
        ("b", "p"), ("j", "s"), ("o", "u"),
    ):
        t = t.replace(a, b)
    t = re.sub(r"(.)\1+", r"\1", t)  # collapse doubled letters
    t = re.sub(r"[^a-z0-9 ]", "", t)
    return _SPACE.sub(" ", t).strip()

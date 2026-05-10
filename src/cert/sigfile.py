"""ADR-036 §3.4 — load/save the binary `.sig` file.

Format (ASCII, LF line endings):
    CAESIGv01\\n
    algo=ed25519\\n
    pubkey_fp=<hex 64>\\n
    sig=<base64 88 chars>\\n
"""
from __future__ import annotations

import base64
from dataclasses import dataclass
from pathlib import Path

HEADER = "CAESIGv01"
SUPPORTED_ALGOS = ("ed25519",)


@dataclass(frozen=True)
class SigFile:
    algo: str
    pubkey_fingerprint: str  # hex 64
    signature: bytes  # 64 bytes for Ed25519


def write(path: Path, sf: SigFile) -> None:
    if sf.algo not in SUPPORTED_ALGOS:
        raise ValueError(f"unsupported algo {sf.algo!r}")
    sig_b64 = base64.b64encode(sf.signature).decode("ascii")
    body = (
        f"{HEADER}\n"
        f"algo={sf.algo}\n"
        f"pubkey_fp={sf.pubkey_fingerprint}\n"
        f"sig={sig_b64}\n"
    )
    path.write_text(body, encoding="ascii")


def read(path: Path) -> SigFile:
    text = path.read_text(encoding="ascii")
    lines = text.splitlines()
    if not lines or lines[0] != HEADER:
        raise ValueError(f"missing or wrong header {HEADER!r}")
    fields: dict[str, str] = {}
    for line in lines[1:]:
        if not line:
            continue
        if "=" not in line:
            raise ValueError(f"malformed line {line!r}")
        k, _, v = line.partition("=")
        fields[k] = v
    for required in ("algo", "pubkey_fp", "sig"):
        if required not in fields:
            raise ValueError(f"missing field {required!r}")
    if fields["algo"] not in SUPPORTED_ALGOS:
        raise ValueError(f"unsupported algo {fields['algo']!r}")
    sig = base64.b64decode(fields["sig"], validate=True)
    if fields["algo"] == "ed25519" and len(sig) != 64:
        raise ValueError(f"Ed25519 signature must be 64 bytes, got {len(sig)}")
    return SigFile(algo=fields["algo"], pubkey_fingerprint=fields["pubkey_fp"], signature=sig)

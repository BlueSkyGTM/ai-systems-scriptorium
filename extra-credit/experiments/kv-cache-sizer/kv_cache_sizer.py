#!/usr/bin/env python3
"""KV-cache sizer — back-of-envelope GPU memory for a transformer's KV cache.

The KV cache is the per-token state an inference engine keeps so it doesn't
recompute attention over the whole prefix every step. It is the memory that
paged KV-cache (vLLM's PagedAttention) exists to pack efficiently, and the
number that decides how many concurrent sequences a card can hold.

    bytes = 2 (K and V) * layers * seq_len * kv_heads * head_dim * dtype_bytes * batch

GQA/MQA shrink it by sharing KV across query heads (kv_heads < attn_heads).
Stdlib only; offline. Educational, not a profiler.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass

DTYPE_BYTES = {"fp32": 4, "fp16": 2, "bf16": 2, "fp8": 1, "int8": 1, "int4": 0.5}


@dataclass(frozen=True)
class Model:
    name: str
    layers: int
    kv_heads: int          # KV heads (== attn heads when no GQA)
    head_dim: int


# A few public-spec presets so the tool is useful out of the box.
PRESETS = {
    "llama3-8b": Model("Llama 3 8B", layers=32, kv_heads=8, head_dim=128),
    "llama3-70b": Model("Llama 3 70B", layers=80, kv_heads=8, head_dim=128),
    "mistral-7b": Model("Mistral 7B", layers=32, kv_heads=8, head_dim=128),
}


def kv_cache_bytes(m: Model, seq_len: int, batch: int, dtype: str) -> float:
    return 2 * m.layers * seq_len * m.kv_heads * m.head_dim * DTYPE_BYTES[dtype] * batch


def human(num_bytes: float) -> str:
    gb = num_bytes / 1024**3
    if gb >= 1:
        return f"{gb:.2f} GiB"
    return f"{num_bytes / 1024**2:.1f} MiB"


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--model", choices=sorted(PRESETS), default="llama3-8b")
    p.add_argument("--seq-len", type=int, default=8192, help="context length (tokens)")
    p.add_argument("--batch", type=int, default=1, help="concurrent sequences")
    p.add_argument("--dtype", choices=sorted(DTYPE_BYTES), default="fp16")
    args = p.parse_args()

    m = PRESETS[args.model]
    total = kv_cache_bytes(m, args.seq_len, args.batch, args.dtype)
    per_tok = kv_cache_bytes(m, 1, 1, args.dtype)

    print(f"{m.name}  ·  {args.dtype}  ·  seq_len={args.seq_len}  ·  batch={args.batch}")
    print(f"  per token, per sequence : {human(per_tok)}")
    print(f"  KV cache total          : {human(total)}")
    print(f"  on an 80 GiB card, headroom for ~{int(80 * 1024**3 / (per_tok * args.seq_len))} "
          f"sequences of this length")


if __name__ == "__main__":
    main()

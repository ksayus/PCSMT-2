"""数值与格式化工具（替代旧版 size_change.py / numbers.py）。"""

from __future__ import annotations

import decimal


def round_half_up(number: float | str, ndigits: int = 0) -> float | int:
    """四舍五入（ROUND_HALF_UP），避免银行家舍入。"""
    context = decimal.getcontext()
    original = context.rounding
    context.rounding = decimal.ROUND_HALF_UP
    try:
        if isinstance(number, float):
            number = repr(number)
        quantized = decimal.Decimal(number).quantize(
            decimal.Decimal(f"1e-{ndigits}"))
        return float(quantized) if ndigits > 0 else int(quantized)
    finally:
        context.rounding = original


def human_readable_size(size_bytes: float) -> str:
    """字节数转可读字符串，如 ``54.89MB``（与旧版输出格式一致）。"""
    size = float(size_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024:
            return f"{round_half_up(size, 2)}{unit}"
        size /= 1024
    return f"{round_half_up(size, 2)}PB"

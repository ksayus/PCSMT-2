import decimal

def round_half_up(number, ndigits=0):
    # 设置舍入模式为ROUND_HALF_UP
    context = decimal.getcontext()
    original_rounding = context.rounding  # 保存原舍入方式以便后续恢复
    context.rounding = decimal.ROUND_HALF_UP

    try:
        # 将浮点数转换为字符串以避免精度问题
        if isinstance(number, float):
            number = repr(number)
        decimal_number = decimal.Decimal(number)
        # 构造量化单位，例如ndigits=2则为'0.01'
        quantized = decimal_number.quantize(decimal.Decimal('1e-{}'.format(ndigits)))
        # 转换为int或float返回
        size = float(quantized) if ndigits > 0 else int(quantized)
    finally:
        context.rounding = original_rounding  # 恢复原舍入方式

    return size

def size_change(size):
    size_types = ['B', 'KB', 'MB', 'GB', 'TB']
    for size_type in size_types:
        if size < 1024:
            return str(round_half_up(size, 2)) + size_type
        else:
            size = size / 1024
            continue
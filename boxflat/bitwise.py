def test_bit(value, bit_number: int) -> bool:
    if bit_number < 0:
        return

    return bool(value >> bit_number & 1)


def modify_bit(value, bit_number: int, set_bit=True) -> int:
    if bit_number < 0:
        return

    bit = 1 << bit_number

    if set_bit:
        value |= bit
    else:
        value &= ~bit

    return value


def set_bit(value, bit_number: int) -> int:
    return modify_bit(value, bit_number, set_bit=True)


def unset_bit(value, bit_number: int) -> int:
    return modify_bit(value, bit_number, set_bit=False)

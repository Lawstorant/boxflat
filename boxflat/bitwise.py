# Copyright (c) 2025, Tomasz Pakuła Using Arch BTW

def test_bit(value: int, bit_number: int) -> bool:
    if bit_number < 0:
        return

    return bool(value >> bit_number & 1)


def modify_bit(value: int, bit_number: int, set_bit=True) -> int:
    if bit_number < 0:
        return

    bit = 1 << bit_number

    if set_bit:
        value |= bit
    else:
        value &= ~bit

    return value


def set_bit(value: int, bit_number: int) -> int:
    return modify_bit(value, bit_number, set_bit=True)


def unset_bit(value: int, bit_number: int) -> int:
    return modify_bit(value, bit_number, set_bit=False)


def toggle_bit(value: int, bit_number: int) -> int:
    return value ^ (1 << bit_number)


def bit(bit_number: int) -> int:
    return set_bit(0, bit_number)


def swap_nibbles(value: int) -> int:
    ret = (value & 0x0f) << 4
    ret |= (value & 0xf0) >> 4
    return ret

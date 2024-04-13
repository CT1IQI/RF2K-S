BASE = 256


def extract_value(data):
    return data[4] * BASE * BASE * BASE + data[5] * BASE * BASE + data[6] * BASE + data[7]

def convert_to_message_data(prefix, value):
    bit4 = int(value / (BASE * BASE * BASE))
    bit3 = int(value / (BASE * BASE) - bit4 * BASE)
    bit2 = int(value / BASE - bit4 * BASE * BASE - bit3 * BASE)
    bit1 = int(value - bit4 * BASE * BASE * BASE - bit3 * BASE * BASE - bit2 * BASE)
    value_as_byte = [bit4, bit3, bit2, bit1]
    return prefix + value_as_byte

BASE32_STANDARD_ALPHABET = '0123456789ABCDEFGHIJKLMNOPQRSTUV'


def int_to_b32(number, b32_string_size):
    reversed_value = []

    while number != 0:
        number, i = divmod(number, len(BASE32_STANDARD_ALPHABET))
        reversed_value.append(BASE32_STANDARD_ALPHABET[i])

    while len(reversed_value) < b32_string_size:
        reversed_value.append('0')

    return ''.join(reversed(reversed_value))

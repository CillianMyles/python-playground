"""
Soundex algorithm implementation.
Based on: https://code.activestate.com/recipes/52213-soundex-algorithm
Adapted to match: https://www.archives.gov/research/census/soundex
"""

# soundex values for the alphabet
_DIGITS = "0123012H02245501262301W202"
_LENGTH = 4


def soundex(
    input: str,
    digits: str = _DIGITS,
    length: int = _LENGTH,
) -> str:
    output = ""
    char_0 = ""

    # translate alpha characters in input to soundex digits
    for char in input.upper():
        if char.isalpha():
            # remember first letter
            if not char_0:
                char_0 = char
            digit = digits[ord(char) - ord("A")]
            # duplicate consecutive soundex digits are skipped
            if not output or (digit not in [output[-1], "H", "W"]):
                output += digit

    # replace first digit with first alpha character
    output = char_0 + output[1:]

    # remove all 0s from the soundex code
    output = output.replace("0", "")

    # return soundex code padded to length characters
    return (output + length * "0")[:length]

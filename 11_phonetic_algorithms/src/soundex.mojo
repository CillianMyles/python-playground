"""
Soundex algorithm implementation.
Based on: https://code.activestate.com/recipes/52213-soundex-algorithm
Adapted to match: https://www.archives.gov/research/census/soundex
"""

# soundex values for the alphabet
alias _DIGITS = "0123012H02245501262301W202"
alias _LENGTH = 4

fn soundex(
    input: String, 
    digits: String = _DIGITS, 
    length: Int = _LENGTH,
) -> String:
    var output = ""
    var char_0 = ""

    # translate alpha characters in input to soundex digits
    for char in input.upper().codepoints():
        var char_str = String(char)
        var char_code = ord(char_str)
        if char_code >= ord("A") and char_code <= ord("Z"):
            # remember first letter
            if char_0 == "":
                char_0 = char_str

            var index = char_code - ord("A")
            var digit = String(digits[index])

            # duplicate consecutive soundex digits are skipped
            if len(output) == 0 or (digit != output[-1] and digit != "H" and digit != "W"):
                output += digit

    # replace first digit with first alpha character
    if len(output) > 0:
        var tail = ""
        if len(output) > 1:
            tail = output[1:]
        output = char_0 + tail

    # remove all "0"s from the soundex code
    output = output.replace("0", "")

    # pad with zeros and slice
    return (output + "0" * length)[:length]

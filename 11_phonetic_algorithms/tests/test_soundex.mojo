from testing import assert_equal
from soundex import soundex


def test_soundex_standard_cases():
    assert_equal(soundex("Robert"), "R163")
    assert_equal(soundex("Rupert"), "R163")
    assert_equal(soundex("Smith"), "S530")
    assert_equal(soundex("Smyth"), "S530")


def test_soundex_double_letters():
    assert_equal(soundex("Gutierrez"), "G362")


def test_soundex_repeat_output_numbers():
    assert_equal(soundex("Pfister"), "P236")
    assert_equal(soundex("Jackson"), "J250")
    assert_equal(soundex("Tymczak"), "T522")


def test_soundex_repeat_consonant_separators():
    assert_equal(soundex("Tymczak"), "T522")
    assert_equal(soundex("Ashcraft"), "A261")

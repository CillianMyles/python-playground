from src.soundex import soundex


def test_soundex_standard_cases():
    assert soundex("Robert") == "R163"
    assert soundex("Rupert") == "R163"
    assert soundex("Smith") == "S530"
    assert soundex("Smyth") == "S530"


def test_soundex_double_letters():
    assert soundex("Gutierrez") == "G362"


def test_soundex_repeat_output_numbers():
    assert soundex("Pfister") == "P236"
    assert soundex("Jackson") == "J250"
    assert soundex("Tymczak") == "T522"


def test_soundex_repeat_consonant_separators():
    assert soundex("Tymczak") == "T522"
    assert soundex("Ashcraft") == "A261"

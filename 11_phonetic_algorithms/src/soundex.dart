/// Soundex algorithm implementation (in Dart).
/// Based on: https://code.activestate.com/recipes/52213-soundex-algorithm
/// Adapted to match: https://www.archives.gov/research/census/soundex

// soundex values for the alphabet
const _DIGITS = "0123012H02245501262301W202";
const _LENGTH = 4;

const _CHAR_0 = 48;
const _CHAR_A = 65;
const _CHAR_Z = 90;

String soundex(String input, {String digits = _DIGITS, int length = _LENGTH}) {
  var output = "";
  var firstLetter = "";

  for (final char in input.toUpperCase().runes) {
    if (char < _CHAR_A || char > _CHAR_Z) {
      continue;
    }

    if (firstLetter.isEmpty) {
      firstLetter = String.fromCharCode(char);
      output += firstLetter;
      continue;
    }

    final digit = digits.codeUnitAt(char - _CHAR_A);
    if (digit != _CHAR_0 && digit != output.codeUnitAt(output.length - 1)) {
      output += String.fromCharCode(digit);
    }
    
    if (output.length == length) {
      break;
    }
  }

  return output.padRight(length, '0');
}

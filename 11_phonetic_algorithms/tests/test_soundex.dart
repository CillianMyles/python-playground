import 'package:test/test.dart';
import 'package:soundex/soundex.dart';

void main() {
  group('Soundex', () {
    test('standard cases', () {
      expect(soundex("Robert"), equals("R163"));
      expect(soundex("Rupert"), equals("R163"));
      expect(soundex("Smith"), equals("S530"));
      expect(soundex("Smyth"), equals("S530"));
    });

    test('double letters', () {
      expect(soundex("Gutierrez"), equals("G362"));
    });

    test('repeat output numbers', () {
      expect(soundex("Pfister"), equals("P236"));
      expect(soundex("Jackson"), equals("J250"));
      expect(soundex("Tymczak"), equals("T522"));
    });

    test('repeat consonant separators', () {
      expect(soundex("Pfister"), equals("P236"));
      expect(soundex("Ashcraft"), equals("A261"));
    });
  });
}

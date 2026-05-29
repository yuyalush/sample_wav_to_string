import unittest

from transcribe_compare import compare_texts, normalize_text


class CompareTextTests(unittest.TestCase):
    def test_normalize_text_removes_spaces_and_lowercases(self):
        self.assertEqual(normalize_text(" A b C  "), "abc")

    def test_compare_texts_exact_match_after_normalization(self):
        result = compare_texts("テ スト", "テスト")
        self.assertTrue(result.exact_match)
        self.assertAlmostEqual(result.similarity, 100.0)

    def test_compare_texts_similarity_when_different(self):
        result = compare_texts("こんにちは", "こんばんは")
        self.assertFalse(result.exact_match)
        self.assertLess(result.similarity, 100.0)


if __name__ == "__main__":
    unittest.main()

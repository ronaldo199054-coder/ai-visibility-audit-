import unittest

from ai_visibility_audit.audit import find_mentions


class TestMention(unittest.TestCase):
    def test_brand_mentioned(self):
        self.assertEqual(
            find_mentions("可以看看示例品牌，口碑不错", ["示例品牌", "ExampleBrand"]),
            ["示例品牌"],
        )

    def test_not_mentioned(self):
        self.assertEqual(find_mentions("推荐竞品B", ["示例品牌"]), [])

    def test_case_insensitive(self):
        self.assertEqual(find_mentions("Try EXAMPLEBRAND today", ["ExampleBrand"]), ["ExampleBrand"])


if __name__ == "__main__":
    unittest.main()

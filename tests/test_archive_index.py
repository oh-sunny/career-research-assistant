import json
import tempfile
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.archive_index import build_summary, load_index, normalize_url  # noqa: E402


class ArchiveIndexTests(unittest.TestCase):
    def test_normalize_url_removes_tracking_and_fragment(self):
        normalized = normalize_url(
            "HTTPS://Example.COM/article/?b=2&utm_source=test&a=1#section"
        )
        parts = urlsplit(normalized)
        self.assertEqual(parts.scheme, "https")
        self.assertEqual(parts.netloc, "example.com")
        self.assertEqual(parts.path, "/article")
        self.assertEqual(parse_qs(parts.query), {"a": ["1"], "b": ["2"]})
        self.assertEqual(parts.fragment, "")

    def test_load_index_rejects_missing_fields(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "index.jsonl"
            path.write_text(json.dumps({"canonical_url": "https://example.com"}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "필수 필드"):
                load_index(path)

    def test_build_summary_counts_roles_and_areas(self):
        records = [
            {
                "purpose": "직무 공부",
                "roles": ["MD"],
                "work_areas": ["고객·시장 분석", "판매 전략"],
            },
            {
                "purpose": "산업·기업 동향",
                "roles": ["HR"],
                "work_areas": ["HR 데이터"],
            },
        ]
        summary = build_summary(records)
        self.assertEqual(summary["total"], 2)
        self.assertEqual(summary["by_role"], {"HR": 1, "MD": 1})
        self.assertEqual(summary["by_work_area"]["HR 데이터"], 1)


if __name__ == "__main__":
    unittest.main()

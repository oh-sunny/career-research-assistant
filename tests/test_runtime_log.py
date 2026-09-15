import unittest
from datetime import datetime, timedelta, timezone

from scripts.runtime_log import prune_records


class RuntimeLogTests(unittest.TestCase):
    def test_prune_records_keeps_only_last_90_days(self):
        now = datetime(2026, 9, 15, tzinfo=timezone.utc)
        records = [
            {"url": "https://example.com/recent", "checked_at": (now - timedelta(days=89)).isoformat()},
            {"url": "https://example.com/old", "checked_at": (now - timedelta(days=91)).isoformat()},
        ]
        kept = prune_records(records, "checked_at", now)
        self.assertEqual([record["url"] for record in kept], ["https://example.com/recent"])

    def test_prune_records_drops_missing_timestamp(self):
        now = datetime(2026, 9, 15, tzinfo=timezone.utc)
        self.assertEqual(prune_records([{"url": "https://example.com"}], "checked_at", now), [])


if __name__ == "__main__":
    unittest.main()

import json
import unittest
from datetime import date
from unittest.mock import patch

from scripts import notion_reader
from scripts.settings import NotionSettings


class _FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


class NotionReaderTests(unittest.TestCase):
    @patch.object(notion_reader.urllib.request, "urlopen")
    def test_queries_korean_day_and_ai_collection_path(self, urlopen):
        urlopen.return_value = _FakeResponse(
            {
                "results": [
                    {
                        "created_time": "2026-09-28T01:00:00.000Z",
                        "url": "https://notion.so/page",
                        "properties": {
                            "자료명": {
                                "title": [{"plain_text": "HR 인터뷰"}]
                            },
                            "핵심 요약": {
                                "rich_text": [{"plain_text": "실무 요약"}]
                            },
                            "관련 직무": {"multi_select": [{"name": "HR"}]},
                            "업무 영역": {
                                "multi_select": [{"name": "채용·온보딩"}]
                            },
                            "원문 링크": {"url": "https://example.com/hr"},
                        },
                    }
                ],
                "has_more": False,
                "next_cursor": None,
            }
        )

        records = notion_reader.query_ai_collected_pages(
            date(2026, 9, 28),
            settings=NotionSettings("notion-token", "data-source-id"),
        )

        self.assertEqual(records[0]["title"], "HR 인터뷰")
        self.assertEqual(records[0]["roles"], ["HR"])
        request = urlopen.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))
        filters = payload["filter"]["and"]
        self.assertEqual(filters[0]["created_time"]["on_or_after"], "2026-09-27T15:00:00Z")
        self.assertEqual(filters[1]["created_time"]["before"], "2026-09-28T15:00:00Z")
        self.assertEqual(filters[2]["select"]["equals"], "AI 서칭")
        self.assertEqual(request.get_header("Notion-version"), notion_reader.NOTION_VERSION)


if __name__ == "__main__":
    unittest.main()

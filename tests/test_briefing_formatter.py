import unittest
from datetime import date

from scripts.briefing_formatter import format_daily_briefing


class BriefingFormatterTests(unittest.TestCase):
    def test_formats_counts_links_and_optional_mention(self):
        message = format_daily_briefing(
            [
                {
                    "title": "채용 담당자 인터뷰",
                    "summary": "지원자 경험을 기준으로 채용 과정을 개선했다.",
                    "roles": ["HR"],
                    "work_areas": ["채용·온보딩"],
                    "source_url": "https://example.com/source",
                    "notion_url": "https://notion.so/page",
                }
            ],
            date(2026, 9, 28),
            mention_user_id="U123",
        )

        self.assertIn("<@U123>", message)
        self.assertIn("오늘 저장 1건 · HR 1건 · MD 0건", message)
        self.assertIn("<https://example.com/source|원문>", message)
        self.assertIn("<https://notion.so/page|Notion>", message)

    def test_explains_when_no_pages_are_available(self):
        message = format_daily_briefing([], date(2026, 9, 28))

        self.assertIn("오늘 저장 0건", message)
        self.assertIn("웹 예약의 실행 결과", message)


if __name__ == "__main__":
    unittest.main()

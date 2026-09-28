import os
import tempfile
import unittest
from pathlib import Path

from scripts.settings import get_slack_settings, load_env_file


class SettingsTests(unittest.TestCase):
    def setUp(self):
        self.original_token = os.environ.pop("SLACK_BOT_TOKEN", None)
        self.original_channel = os.environ.pop("SLACK_CHANNEL_ID", None)
        self.original_mention = os.environ.pop("SLACK_MENTION_USER_ID", None)
        self.original_notion_key = os.environ.pop("NOTION_API_KEY", None)
        self.original_data_source = os.environ.pop("NOTION_DATA_SOURCE_ID", None)

    def tearDown(self):
        os.environ.pop("SLACK_BOT_TOKEN", None)
        os.environ.pop("SLACK_CHANNEL_ID", None)
        os.environ.pop("SLACK_MENTION_USER_ID", None)
        os.environ.pop("NOTION_API_KEY", None)
        os.environ.pop("NOTION_DATA_SOURCE_ID", None)
        if self.original_token is not None:
            os.environ["SLACK_BOT_TOKEN"] = self.original_token
        if self.original_channel is not None:
            os.environ["SLACK_CHANNEL_ID"] = self.original_channel
        if self.original_mention is not None:
            os.environ["SLACK_MENTION_USER_ID"] = self.original_mention
        if self.original_notion_key is not None:
            os.environ["NOTION_API_KEY"] = self.original_notion_key
        if self.original_data_source is not None:
            os.environ["NOTION_DATA_SOURCE_ID"] = self.original_data_source

    def test_reads_slack_values_from_env_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text(
                "SLACK_BOT_TOKEN=test-token\nSLACK_CHANNEL_ID=C123456\n",
                encoding="utf-8",
            )

            settings = get_slack_settings(env_path)

            self.assertEqual(settings.bot_token, "test-token")
            self.assertEqual(settings.channel_id, "C123456")
            self.assertTrue(settings.is_configured)

    def test_reads_notion_values_from_env_file(self):
        from scripts.settings import get_notion_settings

        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text(
                "NOTION_API_KEY=notion-token\n"
                "NOTION_DATA_SOURCE_ID=data-source-id\n",
                encoding="utf-8",
            )

            settings = get_notion_settings(env_path)

            self.assertEqual(settings.api_key, "notion-token")
            self.assertEqual(settings.data_source_id, "data-source-id")
            self.assertTrue(settings.is_configured)

    def test_existing_environment_value_has_priority(self):
        os.environ["SLACK_BOT_TOKEN"] = "system-token"
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text("SLACK_BOT_TOKEN=file-token\n", encoding="utf-8")

            load_env_file(env_path)

            self.assertEqual(os.environ["SLACK_BOT_TOKEN"], "system-token")


if __name__ == "__main__":
    unittest.main()

import os
import tempfile
import unittest
from pathlib import Path

from scripts.settings import get_slack_settings, load_env_file


class SettingsTests(unittest.TestCase):
    def setUp(self):
        self.original_token = os.environ.pop("SLACK_BOT_TOKEN", None)
        self.original_channel = os.environ.pop("SLACK_CHANNEL_ID", None)

    def tearDown(self):
        os.environ.pop("SLACK_BOT_TOKEN", None)
        os.environ.pop("SLACK_CHANNEL_ID", None)
        if self.original_token is not None:
            os.environ["SLACK_BOT_TOKEN"] = self.original_token
        if self.original_channel is not None:
            os.environ["SLACK_CHANNEL_ID"] = self.original_channel

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

    def test_existing_environment_value_has_priority(self):
        os.environ["SLACK_BOT_TOKEN"] = "system-token"
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text("SLACK_BOT_TOKEN=file-token\n", encoding="utf-8")

            load_env_file(env_path)

            self.assertEqual(os.environ["SLACK_BOT_TOKEN"], "system-token")


if __name__ == "__main__":
    unittest.main()

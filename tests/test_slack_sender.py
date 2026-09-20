import io
import json
import unittest
from unittest.mock import patch

from scripts import slack_sender
from scripts.settings import SlackSettings


class _FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return json.dumps({"ok": True, "channel": "C123", "ts": "1.2"}).encode()


class SlackSenderTests(unittest.TestCase):
    @patch.object(slack_sender, "get_slack_settings")
    @patch.object(slack_sender.urllib.request, "urlopen")
    def test_posts_message_to_configured_channel(self, urlopen, get_settings):
        get_settings.return_value = SlackSettings("test-token", "C123")
        urlopen.return_value = _FakeResponse()

        result = slack_sender.post_message("테스트 메시지")

        self.assertTrue(result["ok"])
        request = urlopen.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(payload["channel"], "C123")
        self.assertEqual(payload["text"], "테스트 메시지")
        self.assertEqual(request.get_header("Authorization"), "Bearer test-token")

    @patch.object(slack_sender, "get_slack_settings")
    def test_rejects_missing_settings(self, get_settings):
        get_settings.return_value = SlackSettings("", "")

        with self.assertRaises(slack_sender.SlackSendError):
            slack_sender.post_message("테스트")


if __name__ == "__main__":
    unittest.main()

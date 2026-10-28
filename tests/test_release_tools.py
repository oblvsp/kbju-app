import base64
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import build_app
import publish_github


class BuildAppTests(unittest.TestCase):
    def test_build_uses_repo_data_when_called_from_another_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            old_cwd = Path.cwd()
            try:
                os.chdir(tmp)
                output = Path(tmp) / "nested" / "calculator.html"
                build_app.main(build=17, version="test", out=output)
            finally:
                os.chdir(old_cwd)

            html = output.read_text(encoding="utf-8")
            self.assertIn('data-app="kbju-calculator"', html)
            self.assertIn("var APP_BUILD = 17;", html)
            self.assertIn("function updateUrl(url)", html)
            self.assertIn("_kbju_ts=", html)
            self.assertIn("raw.githubusercontent.com/oblvsp/kbju-app/main/update.json", html)
            self.assertIn("var expectedBuild = 'var APP_BUILD = ' + remoteBuild", html)
            self.assertNotIn("__DATA__", html)


class PublisherTests(unittest.TestCase):
    def test_token_is_passed_as_ephemeral_git_header_not_remote_url(self):
        with patch.dict(os.environ, {"GITHUB_TOKEN": "secret-test-token"}, clear=False):
            env = publish_github.git_environment({})
        self.assertEqual(env["GIT_CONFIG_KEY_0"], "http.extraheader")
        self.assertNotIn("secret-test-token", env["GIT_CONFIG_VALUE_0"])
        self.assertIn("secret-test-token", base64.b64decode(
            env["GIT_CONFIG_VALUE_0"].split()[-1]
        ).decode())

    def test_json_writer_uses_utf8_and_newline(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "update.json"
            publish_github.save_json(output, {"notes": "исправление", "build": 12})
            raw = output.read_text(encoding="utf-8")
        self.assertTrue(raw.endswith("\n"))
        self.assertIn("исправление", raw)

    def test_remote_manifest_build_takes_precedence_over_stale_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            (work / "update.json").write_text('{"build": 12}', encoding="utf-8")
            with patch.object(publish_github, "WORK", work):
                self.assertEqual(publish_github.published_build(10), 12)


if __name__ == "__main__":
    unittest.main()

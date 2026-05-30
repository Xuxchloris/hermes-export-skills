from __future__ import annotations

import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from trade_utils import fetch_url  # noqa: E402


class ScrapingBackendTests(unittest.TestCase):
    def test_http_backend_reads_file_url_when_explicitly_configured(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            html_path = Path(temp_dir) / "index.html"
            html_path.write_text("<html><body>hello</body></html>", encoding="utf-8")

            html = fetch_url(html_path.as_uri(), {"engine": "http"})

            self.assertIn("hello", html)

    def test_default_backend_uses_scrapling_fetcher(self) -> None:
        fake_page = Mock()
        fake_page.html_content = "<html>scrapling default</html>"
        with patch("scrapling.fetchers.Fetcher.get", return_value=fake_page) as get:
            html = fetch_url("https://example.com")

        self.assertIn("scrapling default", html)
        get.assert_called_once()

    def test_scrapling_backend_reports_dependency_hint_when_missing(self) -> None:
        with patch("builtins.__import__", side_effect=ModuleNotFoundError("No module named 'scrapling'")):
            with self.assertRaisesRegex(RuntimeError, "requirements.txt"):
                fetch_url("https://example.com")


if __name__ == "__main__":
    unittest.main()

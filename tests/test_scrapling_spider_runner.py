from __future__ import annotations

import csv
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from threading import Thread
import unittest

from scrapling.spiders import Spider


ROOT = Path(__file__).resolve().parents[1]


class ScraplingSpiderRunnerTests(unittest.TestCase):
    def run_script(self, script: str, *args: str) -> subprocess.CompletedProcess[str]:
        command = [sys.executable, str(ROOT / "tools" / script), *args]
        return subprocess.run(command, cwd=ROOT, capture_output=True, text=True)

    def test_native_spider_runner_outputs_prospects_and_report(self) -> None:
        from tools.scrapling_spider_runner import ProspectDiscoverySpider

        self.assertTrue(issubclass(ProspectDiscoverySpider, Spider))

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802 - stdlib callback name.
                pages = {
                    "/exhibitors": (
                        "<html><body>"
                        "<h1>Outdoor retail exhibitors</h1>"
                        "<p>Folding camping table buyers, distributors, and importers.</p>"
                        '<a href="https://alpha-buyer.example">Alpha Import Buyers</a>'
                        '<a href="/beta">Beta Outdoor Distributor</a>'
                        '<a href="mailto:sales@example.test">Email only</a>'
                        "</body></html>"
                    ),
                    "/beta": "<html><body><h1>Beta Outdoor Distributor</h1></body></html>",
                }
                body = pages.get(self.path, "<html><body>missing</body></html>").encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, format: str, *args: object) -> None:
                return

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                discovery = temp_path / "DISCOVERY.yaml"
                discovery.write_text(
                    f"""
discovery_mode: "native_scrapling_spider"
scraping:
  engine: "scrapling-fetcher"
scrapling_spider:
  enabled: true
  robots_txt_obey: false
  concurrent_requests: 2
  concurrent_requests_per_domain: 1
  crawl_delay_seconds: 0
  checkpoint_dir: "{(temp_path / 'checkpoint').as_posix()}"
  source_urls:
    - name: "Local exhibitors"
      url: "http://127.0.0.1:{server.server_port}/exhibitors"
      source_type: "trade_show"
      country: "United States"
""",
                    encoding="utf-8",
                )
                output_dir = temp_path / "out"

                result = self.run_script(
                    "scrapling_spider_runner.py",
                    "--discovery",
                    str(discovery),
                    "--product",
                    str(ROOT / "templates" / "PRODUCT.example.yaml"),
                    "--output-dir",
                    str(output_dir),
                )

                self.assertEqual(result.returncode, 0, result.stderr)
                with (output_dir / "prospects.raw.csv").open(encoding="utf-8") as handle:
                    rows = list(csv.DictReader(handle))
                self.assertEqual(
                    {row["company_name"] for row in rows},
                    {"Alpha Import Buyers", "Beta Outdoor Distributor"},
                )
                self.assertTrue((output_dir / "prospects.raw.json").exists())
                report = json.loads((output_dir / "crawl_report.json").read_text(encoding="utf-8"))
                self.assertEqual(report["discovery_mode"], "native_scrapling_spider")
                self.assertEqual(report["source_status"], "verified")
                self.assertEqual(report["sources_checked"], 1)
                self.assertEqual(report["candidates_found"], 2)
                self.assertGreaterEqual(report["spider_stats"]["requests_count"], 1)
                self.assertIn("scrapling_native_spider", report["runner"])
        finally:
            server.shutdown()
            server.server_close()

    def test_mcp_tool_wraps_native_spider_runner(self) -> None:
        from tools.scrapling_mcp_server import collect_prospects_tool

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802 - stdlib callback name.
                body = (
                    "<html><body>"
                    "<p>Folding camping table distributor list.</p>"
                    '<a href="https://gamma-buyer.example">Gamma Retail Buyer</a>'
                    "</body></html>"
                ).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, format: str, *args: object) -> None:
                return

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                temp_path = Path(temp_dir)
                discovery = temp_path / "DISCOVERY.yaml"
                discovery.write_text(
                    f"""
discovery_mode: "native_scrapling_spider"
scrapling_spider:
  enabled: true
  source_urls:
    - name: "Local file directory"
      url: "http://127.0.0.1:{server.server_port}/directory"
      source_type: "industry_directory"
      country: "United States"
""",
                    encoding="utf-8",
                )
                output_dir = temp_path / "mcp-out"

                result = collect_prospects_tool(
                    discovery_path=str(discovery),
                    product_path=str(ROOT / "templates" / "PRODUCT.example.yaml"),
                    output_dir=str(output_dir),
                )

                self.assertEqual(result["source_status"], "verified")
                self.assertEqual(result["candidates_found"], 1)
                self.assertTrue(Path(result["outputs"]["csv"]).exists())
            finally:
                server.shutdown()
                server.server_close()

    def test_cli_accepts_runtime_source_url_without_editing_discovery(self) -> None:
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802 - stdlib callback name.
                body = (
                    "<html><body>"
                    "<p>Folding camping table importer directory.</p>"
                    '<a href="https://delta-buyer.example">Delta Import Group</a>'
                    "</body></html>"
                ).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, format: str, *args: object) -> None:
                return

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                discovery = temp_path / "DISCOVERY.yaml"
                discovery.write_text(
                    """
discovery_mode: "search_tasks"
scrapling_spider:
  enabled: false
  source_urls: []
""",
                    encoding="utf-8",
                )
                output_dir = temp_path / "runtime"

                result = self.run_script(
                    "collect_prospects.py",
                    "--discovery",
                    str(discovery),
                    "--product",
                    str(ROOT / "templates" / "PRODUCT.example.yaml"),
                    "--source-url",
                    f"http://127.0.0.1:{server.server_port}/directory",
                    "--source-name",
                    "Agent selected directory",
                    "--source-type",
                    "industry_directory",
                    "--source-country",
                    "United States",
                    "--output-dir",
                    str(output_dir),
                )

                self.assertEqual(result.returncode, 0, result.stderr)
                with (output_dir / "prospects.raw.csv").open(encoding="utf-8") as handle:
                    rows = list(csv.DictReader(handle))
                self.assertEqual(rows[0]["company_name"], "Delta Import Group")
                report = json.loads((output_dir / "crawl_report.json").read_text(encoding="utf-8"))
                self.assertEqual(report["runtime_sources_count"], 1)
        finally:
            server.shutdown()
            server.server_close()

    def test_mcp_tool_accepts_runtime_source_urls(self) -> None:
        from tools.scrapling_mcp_server import collect_prospects_tool

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802 - stdlib callback name.
                body = (
                    "<html><body>"
                    "<p>Folding camping table wholesale buyers.</p>"
                    '<a href="https://epsilon-buyer.example">Epsilon Wholesale Buyer</a>'
                    "</body></html>"
                ).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, format: str, *args: object) -> None:
                return

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                discovery = temp_path / "DISCOVERY.yaml"
                discovery.write_text("discovery_mode: \"search_tasks\"\n", encoding="utf-8")
                output_dir = temp_path / "mcp-runtime"

                result = collect_prospects_tool(
                    discovery_path=str(discovery),
                    product_path=str(ROOT / "templates" / "PRODUCT.example.yaml"),
                    output_dir=str(output_dir),
                    source_urls=[
                        {
                            "url": f"http://127.0.0.1:{server.server_port}/directory",
                            "name": "Agent runtime directory",
                            "source_type": "industry_directory",
                            "country": "United States",
                        }
                    ],
                )

                self.assertEqual(result["source_status"], "verified")
                self.assertEqual(result["runtime_sources_count"], 1)
                self.assertTrue(Path(result["outputs"]["csv"]).exists())
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main()

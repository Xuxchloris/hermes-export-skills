from __future__ import annotations

from pathlib import Path
from typing import Any

try:  # Support both script and package imports.
    from .scrapling_spider_runner import run_spider
except ImportError:  # pragma: no cover - script execution path.
    from scrapling_spider_runner import run_spider


def collect_prospects_tool(
    discovery_path: str,
    product_path: str,
    output_dir: str,
    product_query: str = "",
    sku: str = "",
    source_urls: list[str | dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Run native Scrapling prospect discovery and return output paths."""
    return run_spider(
        discovery_path=Path(discovery_path),
        product_path=Path(product_path),
        output_dir=Path(output_dir),
        product_query=product_query,
        sku=sku,
        source_urls=source_urls,
    )


def build_server() -> Any:
    try:
        from mcp.server.fastmcp import FastMCP
    except ModuleNotFoundError as error:  # pragma: no cover - environment dependent.
        raise RuntimeError("Install MCP support with `python -m pip install mcp` before running this server.") from error

    server = FastMCP(
        "hermes-export-scrapling",
        instructions=(
            "Collect overseas prospect candidates from configured public source URLs using "
            "the repository's native Scrapling Spider runner. The tool writes CSV, JSON, "
            "and crawl_report.json files and returns their paths."
        ),
    )

    server.tool(name="collect_prospects")(collect_prospects_tool)
    return server


def main() -> None:
    build_server().run()


if __name__ == "__main__":
    main()

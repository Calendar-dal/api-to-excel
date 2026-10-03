"""Fetch public GitHub repository data and export it to CSV and Excel."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import requests


GITHUB_API_URL = "https://api.github.com"


class ApiExportError(Exception):
    """Raised when API data cannot be fetched or exported."""


def fetch_repositories(user: str, limit: int = 30) -> list[dict[str, Any]]:
    """Fetch a public GitHub user's repositories without authentication."""
    url = f"{GITHUB_API_URL}/users/{user}/repos"
    params = {"per_page": limit, "sort": "updated", "direction": "desc"}
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "api-to-excel-portfolio-project",
    }
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.Timeout as exc:
        raise ApiExportError("The GitHub API request timed out.") from exc
    except requests.ConnectionError as exc:
        raise ApiExportError("Could not connect to the GitHub API.") from exc
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        if status == 404:
            raise ApiExportError(f"GitHub user '{user}' was not found.") from exc
        raise ApiExportError(f"GitHub API returned HTTP {status}.") from exc
    except requests.RequestException as exc:
        raise ApiExportError(f"GitHub API request failed: {exc}") from exc

    try:
        payload = response.json()
    except requests.JSONDecodeError as exc:
        raise ApiExportError("GitHub API returned invalid JSON.") from exc
    if not isinstance(payload, list):
        raise ApiExportError("GitHub API returned an unexpected JSON structure.")
    return payload


def repositories_to_dataframe(repositories: list[dict[str, Any]]) -> pd.DataFrame:
    """Select practical repository fields and build a DataFrame."""
    columns = [
        "name",
        "description",
        "url",
        "language",
        "stars",
        "forks",
        "open_issues",
        "is_fork",
        "archived",
        "updated_at",
    ]
    rows = [
        {
            "name": repo.get("name"),
            "description": repo.get("description"),
            "url": repo.get("html_url"),
            "language": repo.get("language"),
            "stars": repo.get("stargazers_count", 0),
            "forks": repo.get("forks_count", 0),
            "open_issues": repo.get("open_issues_count", 0),
            "is_fork": repo.get("fork", False),
            "archived": repo.get("archived", False),
            "updated_at": repo.get("updated_at"),
        }
        for repo in repositories
    ]
    return pd.DataFrame(rows, columns=columns)


def export_data(data: pd.DataFrame, output_dir: Path, base_name: str) -> tuple[Path, Path]:
    """Export API data to CSV and Excel."""
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / f"{base_name}.csv"
    excel_path = output_dir / f"{base_name}.xlsx"
    try:
        data.to_csv(csv_path, index=False)
        data.to_excel(excel_path, index=False, engine="openpyxl")
    except OSError as exc:
        raise ApiExportError(f"Could not write output files: {exc}") from exc
    return csv_path, excel_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Export a public GitHub user's repositories to CSV and Excel."
    )
    parser.add_argument("--user", required=True, help="Public GitHub username")
    parser.add_argument("--limit", type=int, default=30, choices=range(1, 101))
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        repositories = fetch_repositories(args.user, args.limit)
        data = repositories_to_dataframe(repositories)
        csv_path, excel_path = export_data(
            data, args.output_dir, f"{args.user}_repositories"
        )
    except ApiExportError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Fetched {len(data)} public repositories for '{args.user}'.")
    print(f"CSV output: {csv_path}")
    print(f"Excel output: {excel_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

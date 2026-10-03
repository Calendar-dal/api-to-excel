# API to Excel

Turns public REST API data into practical CSV and Excel deliverables.

**Problem → Solution → Result:** API data is useful but often inconvenient for non-technical users. This command fetches a GitHub user's public repositories, selects decision-friendly fields, and exports spreadsheet-ready files.

## Problem

Teams frequently need data from a web service in a format that can be filtered, shared, or used in a report without writing one-off copy-and-paste scripts.

## Solution

This command-line tool handles HTTP requests, status checks, JSON parsing, field selection, and two spreadsheet formats. It uses the public GitHub API and requires no API key.

## Features

- Configurable GitHub username and result limit
- HTTP status and network error handling
- Clear JSON-to-table field mapping
- CSV and `.xlsx` output
- Offline unit tests using mocked API responses

## Tech Stack

Python 3.11+, requests, pandas, openpyxl, pytest

## Project Structure

```text
api-to-excel/
├── output/
├── src/main.py
├── tests/
├── requirements.txt
└── README.md
```

## Quick Start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
python src/main.py --user octocat --limit 20
```

Run the tests with `python -m pytest`.

## Example

```text
Fetched 8 public repositories for 'octocat'.
CSV output: output\octocat_repositories.csv
Excel output: output\octocat_repositories.xlsx
```

Each row includes the repository name, description, URL, language, stars, forks, issue count, fork/archive status, and last update time.

## Use Cases

- API integration and JSON processing
- Spreadsheet-ready research data
- Repository inventory and reporting
- Repeatable small-business data exports

## Possible Extensions

- Pagination for larger datasets
- Additional public API providers
- Scheduled exports and email delivery

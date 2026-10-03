from pathlib import Path
from unittest.mock import Mock

import pandas as pd
import pytest
import requests

from src.main import ApiExportError, export_data, fetch_repositories, repositories_to_dataframe


def test_fetch_repositories_parses_json(monkeypatch: pytest.MonkeyPatch) -> None:
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = [{"name": "demo", "stargazers_count": 3}]
    get = Mock(return_value=response)
    monkeypatch.setattr(requests, "get", get)

    result = fetch_repositories("octocat", 10)

    assert result[0]["name"] == "demo"
    assert get.call_args.kwargs["timeout"] == 15
    assert get.call_args.kwargs["params"]["per_page"] == 10


def test_http_404_has_clear_error(monkeypatch: pytest.MonkeyPatch) -> None:
    response = Mock(status_code=404)
    error = requests.HTTPError(response=response)
    response.raise_for_status.side_effect = error
    monkeypatch.setattr(requests, "get", Mock(return_value=response))

    with pytest.raises(ApiExportError, match="was not found"):
        fetch_repositories("missing-user")


def test_repositories_become_useful_dataframe() -> None:
    repositories = [
        {
            "name": "demo",
            "description": "Useful project",
            "html_url": "https://github.com/example/demo",
            "language": "Python",
            "stargazers_count": 4,
            "forks_count": 2,
            "open_issues_count": 1,
            "fork": False,
            "archived": False,
            "updated_at": "2026-01-01T00:00:00Z",
        }
    ]

    frame = repositories_to_dataframe(repositories)

    assert frame.loc[0, "language"] == "Python"
    assert frame.loc[0, "stars"] == 4
    assert frame.loc[0, "url"].endswith("/demo")


def test_export_creates_csv_and_excel(tmp_path: Path) -> None:
    frame = pd.DataFrame([{"name": "demo", "stars": 4}])

    csv_path, excel_path = export_data(frame, tmp_path, "repositories")

    assert csv_path.exists()
    assert excel_path.exists()
    assert pd.read_csv(csv_path).loc[0, "name"] == "demo"
    assert pd.read_excel(excel_path).loc[0, "stars"] == 4

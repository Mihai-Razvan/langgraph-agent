from typing import Callable, Any

import requests
import subprocess
from pathlib import Path
from bs4 import BeautifulSoup


def _require_string(kwargs: dict, name: str) -> str | None:
    value = kwargs.get(name)

    if value is None:
        return None

    if not isinstance(value, str):
        return str(value)

    stripped_value = value.strip()
    if not stripped_value:
        return None

    return stripped_value

def fetch_url(**kwargs) -> str:
    url = _require_string(kwargs, "url")

    if url is None:
        return "Missing required parameter: url"

    try:
        response = requests.get(url, timeout=10)
    except Exception as e:
        return str(e)

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "noscript", "svg", "img", "header", "footer", "nav"]):
        tag.decompose()

    parts: list[str] = []

    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    if title:
        parts.append(f"Title: {title}")

    description = soup.find("meta", attrs={"name": "description"})
    if description and description.get("content"):
        parts.append(f"Description: {description['content'].strip()}")

    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines()]
    content = "\n".join(line for line in lines if line)

    if content:
        parts.append("Content:")
        parts.append(content)

    return "\n\n".join(parts)


def read_file(**kwargs) -> str:
    raw_path = _require_string(kwargs, "path")
    if raw_path is None:
        return "Missing required parameter: path"

    path = Path(raw_path)

    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        return str(e)


def list_files(**kwargs) -> str:
    raw_path = _require_string(kwargs, "path") or "."
    path = Path(raw_path)

    try:
        entries = sorted(item.name for item in path.iterdir())
    except Exception as e:
        return str(e)

    return "\n".join(entries)


def create_file(**kwargs) -> str:
    raw_path = _require_string(kwargs, "path")
    if raw_path is None:
        return "Missing required parameter: path"

    content = kwargs.get("content")
    if content is None:
        return "Missing required parameter: content"

    path = Path(raw_path)

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(str(content), encoding="utf-8")
    except Exception as e:
        return str(e)

    return f"Created file: {path}"


def edit_file(**kwargs) -> str:
    raw_path = _require_string(kwargs, "path")
    if raw_path is None:
        return "Missing required parameter: path"

    content = kwargs.get("content")
    if content is None:
        return "Missing required parameter: content"

    path = Path(raw_path)

    if not path.exists():
        return f"File does not exist: {path}"

    if not path.is_file():
        return f"Path is not a file: {path}"

    try:
        path.write_text(str(content), encoding="utf-8")
    except Exception as e:
        return str(e)

    return f"Updated file: {path}"


def execute_bash(**kwargs) -> str:
    command = _require_string(kwargs, "command")
    if command is None:
        return "Missing required parameter: command"

    try:
        result = subprocess.run(
            ["bash", "-lc", command],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except Exception as e:
        return str(e)

    output_parts: list[str] = []

    if result.stdout:
        output_parts.append(result.stdout.strip())

    if result.stderr:
        output_parts.append(result.stderr.strip())

    if result.returncode != 0:
        output_parts.append(f"Exit code: {result.returncode}")

    if not output_parts:
        return "Command completed with no output."

    return "\n".join(output_parts)

available_tools: list[Callable[..., Any]] = [
    fetch_url,
    read_file,
    list_files,
    create_file,
    edit_file,
    execute_bash
]
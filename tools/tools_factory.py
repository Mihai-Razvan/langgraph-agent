from .tool import Tool
from .tools import create_file, edit_file, execute_bash, fetch_url, list_files, read_file


def _build_fetch_url_tool() -> Tool:
    return Tool(
        name="fetch_url",
        description="Fetches and extracts the main readable text content from a webpage URL",
        input_schema={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The full URL of the webpage to fetch (must include http or https)"
                }
            },
            "required": ["url"]
        },
        handler=fetch_url
    )

def _build_read_file_tool() -> Tool:
    return Tool(
        name="read_file",
        description="Reads the contents of a file from disk",
        input_schema={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to read"
                }
            },
            "required": ["path"]
        },
        handler=read_file
    )

def _build_list_files_tool() -> Tool:
    return Tool(
        name="list_files",
        description="Lists files and directories inside a directory",
        input_schema={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Directory path to list. Defaults to the current directory."
                }
            }
        },
        handler=list_files
    )

def _build_create_file_tool() -> Tool:
    return Tool(
        name="create_file",
        description="Creates a file with the provided content",
        input_schema={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to create"
                },
                "content": {
                    "type": "string",
                    "description": "File contents to write"
                }
            },
            "required": ["path", "content"]
        },
        handler=create_file
    )

def _build_edit_file_tool() -> Tool:
    return Tool(
        name="edit_file",
        description="Replaces the contents of an existing file",
        input_schema={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to update"
                },
                "content": {
                    "type": "string",
                    "description": "New file contents to write"
                }
            },
            "required": ["path", "content"]
        },
        handler=edit_file
    )


def _build_execute_bash_tool() -> Tool:
    return Tool(
        name="execute_bash",
        description="Executes a bash command and returns its output",
        input_schema={
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Bash command to execute"
                }
            },
            "required": ["command"]
        },
        handler=execute_bash
    )

def build_tools() -> list[Tool]:
    return [
        _build_fetch_url_tool(),
        _build_read_file_tool(),
        _build_list_files_tool(),
        _build_create_file_tool(),
        _build_edit_file_tool(),
        _build_execute_bash_tool(),
    ]
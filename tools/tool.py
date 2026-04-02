from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Tool:
    name: str
    description: str
    input_schema: dict[str, Any]
    handler: Callable[..., Any]

    def to_anthropic_tool_param(self):
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
            "strict": False
        }

    def run(self, **kwargs) -> Any:
        return self.handler(**kwargs)
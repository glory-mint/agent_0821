from typing import Any

from core.api_client import request


def get_library_tools():
    return request("GET", "/api/agents/library/tools")


def select_library_tool(message: str, tool_choice: str = "auto"):
    payload = {"message": message, "tool_choice": tool_choice}
    return request("POST", "/api/agents/library/select", json=payload)


def run_library_tool(tool_name: str, arguments: dict[str, Any]):
    payload = {"tool_name": tool_name, "arguments": arguments}
    return request("POST", "/api/agents/library/run", json=payload)


def complete_library_agent(message: str, tool_choice: str = "auto"):
    payload = {"message": message, "tool_choice": tool_choice}
    return request("POST", "/api/agents/library/complete", json=payload)


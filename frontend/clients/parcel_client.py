from typing import Any

from core.api_client import request


def get_parcel_tools():
    return request("GET", "/api/agents/parcel/tools")


def select_parcel_tool(message: str, tool_choice: str = "auto"):
    payload = {"message": message, "tool_choice": tool_choice}
    return request("POST", "/api/agents/parcel/select", json=payload)


def run_parcel_tool(tool_name: str, arguments: dict[str, Any]):
    payload = {"tool_name": tool_name, "arguments": arguments}
    return request("POST", "/api/agents/parcel/run", json=payload)


def complete_parcel_agent(message: str, tool_choice: str = "auto"):
    payload = {"message": message, "tool_choice": tool_choice}
    return request("POST", "/api/agents/parcel/complete", json=payload)

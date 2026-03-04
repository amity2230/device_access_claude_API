# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Device MCP is an MCP (Model Context Protocol) server for managing Cisco IOS network devices. It uses FastMCP to expose tools that Claude Desktop (or other MCP clients) can call to list devices, run show commands via SSH, and get AI-powered command suggestions/analysis via OpenAI GPT-4.

## Commands

```bash
# Install dependencies
uv sync

# Run the MCP server (for Claude Desktop or MCP clients)
python device_mcp.py
```

## Architecture

**`device_mcp.py`** — The entire MCP server in a single file. Registers 5 tools with FastMCP:
- `list_devices()` / `get_device_info()` — read from the in-memory `DEVICES` dict (loaded from `devices.yaml`)
- `run_command()` — SSH into a device via Netmiko's `ConnectHandler` and execute a command
- `suggest_commands()` / `analyze_output()` — call OpenAI GPT-4 for AI-powered assistance

**`devices.yaml`** — Device inventory. Each top-level key is a device name mapping to host, device_type, username, password, and description. Loaded once at startup into the global `DEVICES` dict.

**`.env`** — Must contain `OPENAI_API_KEY`. Loaded via `python-dotenv` at startup. Required for the server to start (raises `ValueError` if missing).

**`main.py`** — Unused placeholder entry point; not part of the MCP server.

## Key Dependencies

- **FastMCP 3.x** — MCP protocol framework; tools are registered with `@mcp.tool()` decorator
- **Netmiko** — SSH connections to network devices; uses `ConnectHandler` context manager
- **OpenAI Python SDK** — for `suggest_commands` and `analyze_output` tools
- **PyYAML** — parses `devices.yaml`
- Python 3.13+ required

## Adding Devices

Add a new top-level entry to `devices.yaml` with `host`, `device_type`, `username`, `password` fields. Restart the server to pick up changes. Supported device types follow Netmiko conventions (e.g., `cisco_ios`, `cisco_nxos`, `arista_eos`, `juniper_junos`).

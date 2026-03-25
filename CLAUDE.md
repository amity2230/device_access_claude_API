# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Device MCP is an MCP (Model Context Protocol) server for managing Cisco IOS network devices. It uses FastMCP to expose tools that Claude Desktop (or other MCP clients) can call to list devices, run show commands via SSH, and get AI-powered command suggestions/analysis via the Anthropic Claude API.

## Commands

```bash
# Install dependencies
uv sync

# Run the MCP server (for Claude Desktop or MCP clients)
python device_mcp.py
```

## Architecture

**`device_mcp.py`** — The entire MCP server in a single file. Registers 8 tools with FastMCP:
- `list_devices()` / `get_device_info()` — read from the in-memory `DEVICES` dict (loaded from `devices/*.toml`)
- `run_command()` — SSH into a device via Netmiko's `ConnectHandler` and execute a command
- `suggest_commands()` / `analyze_output()` — call Anthropic Claude API for AI-powered assistance
- `mbss_check()` / `mbss_apply()` / `mbss_audit()` — CPNR MBSS compliance tools

**`devices/`** — Device inventory directory. Each `<device-name>.toml` file defines one device (host, device_type, username, password, description). Loaded at startup via Python's built-in `tomllib`. The filename stem becomes the device name. **Gitignored — never committed.**

**`.env`** — Must contain `ANTHROPIC_API_KEY`. Loaded via `python-dotenv` at startup. Required for the server to start (raises `ValueError` if missing).

**`main.py`** — Standalone CLI chat client using the Anthropic API with tool use; not part of the MCP server.

**`mbss/`** — All MBSS-related files: `mbss_mop.py` (67 control definitions), `CPNR_MBSS.htm`, `CPNR_MBSS.xlsx`, and `cpnr_system_prompt.md`. Imported via `from mbss import MBSS_MOP, MBSS_BY_ID`.

## Key Dependencies

- **FastMCP 3.x** — MCP protocol framework; tools are registered with `@mcp.tool()` decorator
- **Netmiko** — SSH connections to network devices; uses `ConnectHandler` context manager
- **Anthropic Python SDK** — for `suggest_commands` and `analyze_output` tools
- **tomllib** — built-in Python 3.11+ module; parses `devices/*.toml`
- Python 3.13+ required

## Adding Devices

Copy `devices/example-device.toml.template` to `devices/<device-name>.toml`, fill in the fields, and restart the server. The filename stem becomes the device name used in all MCP tools. Required fields: `host`, `device_type`, `username`, `password`. Supported device types follow Netmiko conventions (e.g., `cisco_ios`, `cisco_nxos`, `linux`, `arista_eos`, `juniper_junos`). Device files are gitignored and never committed.

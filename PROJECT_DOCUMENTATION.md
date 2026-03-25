# Device MCP - Complete Project Documentation

**Version:** 1.0.0
**Created:** March 1, 2026
**Project Type:** Model Context Protocol (MCP) Server

---

## Executive Summary

**Device MCP** is a network device management system that provides:
- A **Model Context Protocol (MCP) Server** for Claude Desktop integration
- **Anthropic Claude AI** for intelligent command suggestions and output analysis
- **SSH device connectivity** via Netmiko for executing commands on Linux/Cisco devices
- **MBSS compliance tooling** for auditing and remediating CPNR server security controls

This system allows network operators to manage devices intelligently through Claude Desktop using natural language.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Project Capabilities](#project-capabilities)
3. [Project Structure & Files](#project-structure--files)
4. [Setup Instructions](#setup-instructions)
5. [How to Run](#how-to-run)
6. [Device Interaction Methods](#device-interaction-methods)
7. [MCP Tools Reference](#mcp-tools-reference)
8. [Configuration](#configuration)

---

## System Overview

### Architecture

```
┌──────────────────────────────────┐
│         Claude Desktop           │
│      (MCP Client Interface)      │
└─────────────────┬────────────────┘
                  │ MCP Protocol
       ┌──────────▼──────────┐
       │   device_mcp.py     │
       │   (MCP Server)      │
       └──────┬──────────────┘
              │
    ┌─────────┴──────────┐
    │                    │
┌───▼────┐      ┌────────▼────────┐
│Netmiko │      │  Anthropic      │
│ (SSH)  │      │  Claude API     │
└───┬────┘      │  (Haiku model)  │
    │           └─────────────────┘
┌───▼──────────────────┐
│  Network Devices     │
│ - ubuntu-server      │
│ - rhel-cpnr          │
└──────────────────────┘
```

### Key Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| MCP Framework | FastMCP | 3.0.2+ | Claude Desktop integration |
| SSH Library | Netmiko | 4.6.0+ | Device connectivity |
| AI Model | Anthropic Claude Haiku | claude-haiku-4-5 | Intelligent assistance |
| Config Format | YAML | 6.0.3+ | Device inventory |
| Environment | Python | 3.13+ | Runtime |

---

## Project Capabilities

### Device Management
- **List all devices** - View available network devices
- **Device info** - Get connection details and metadata
- **Command execution** - Run SSH commands on any device in inventory

### Command Execution
- **Show commands** - Read device information (hostname, interfaces, etc.)
- **Config commands** - Execute configuration operations
- **Direct execution** - Run any supported device command

### AI-Powered Features
- **Command suggestions** - Claude suggests commands based on described intent
- **Output analysis** - Claude explains command outputs in plain language

### MBSS Compliance Tools
- **mbss_check** - Verify compliance status of specific CPNR security controls
- **mbss_apply** - Apply remediation for specified controls (pre-check → remediate → post-check)
- **mbss_audit** - Full audit across all 67 CPNR MBSS controls

### Interface
- **Claude Desktop** - Chat-based using MCP protocol (only interface)

---

## Project Structure & Files

```
device-mcp/
├── device_mcp.py           # MCP Server (main application, all 8 tools)
├── devices/                # Device credentials directory (gitignored)
│   ├── ubuntu-server.toml  # Device: ubuntu-server
│   ├── rhel-cpnr.toml      # Device: rhel-cpnr
│   └── example-device.toml.template  # Template for adding new devices
├── .env                    # ANTHROPIC_API_KEY (gitignored)
├── pyproject.toml          # Project dependencies & metadata
├── main.py                 # Standalone CLI chat client (not part of MCP server)
├── client.py               # MCP client utility
├── mbss/                   # MBSS security controls module
│   ├── __init__.py         # Exports MBSS_MOP, MBSS_BY_ID
│   ├── mbss_mop.py         # 67 CPNR MBSS control definitions
│   ├── CPNR_MBSS.htm       # CPNR MBSS reference document
│   ├── CPNR_MBSS.xlsx      # CPNR MBSS spreadsheet
│   └── cpnr_system_prompt.md  # AI system prompt for CPNR context
├── .venv/                  # Python virtual environment
└── uv.lock                 # Dependency lock file
```

---

## File Descriptions

### 1. **device_mcp.py** (MCP Server - Core Application)

**Purpose:** Single-file FastMCP server that exposes 8 tools for device management and MBSS compliance.

**Key Sections:**

#### Imports & Initialization
```python
from fastmcp import FastMCP
from netmiko import ConnectHandler
import yaml, os
import anthropic
from dotenv import load_dotenv
from mbss import MBSS_MOP, MBSS_BY_ID

mcp = FastMCP("DeviceCommands")
load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def load_inventory(path: str = "devices.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

DEVICES = load_inventory()
```
- Sets up FastMCP server instance
- Loads environment variables (including Anthropic API key)
- Initializes Anthropic client
- Loads all devices from `devices.yaml` into the global `DEVICES` dict

#### Available Tools (8 MCP Tools):

**1. list_devices()**
- Returns: Newline-separated list of all device names
- Use Case: See which devices are available in the inventory

**2. run_command(device_name, command)**
- Returns: Command output from the device
- Use Case: Execute any SSH command on a device
- Parameters:
  - `device_name`: Device name from inventory (use `list_devices()` first)
  - `command`: Command to execute on the device

**3. get_device_info(device_name)**
- Returns: Device connection details as a dictionary (host, device_type, etc.)
- Use Case: Verify device connection details

**4. suggest_commands(device_name, intent)**
- Returns: Claude-suggested commands for the described intent
- Use Case: Get AI command recommendations
- Parameters:
  - `device_name`: Target device
  - `intent`: What you want to accomplish (e.g., "show all interfaces")
- **Uses Anthropic Claude API**

**5. analyze_output(device_name, command, output)**
- Returns: AI-generated explanation of command output
- Use Case: Understand complex command output
- Parameters:
  - `device_name`: Device that ran the command
  - `command`: Command that was executed
  - `output`: Raw output to analyze
- **Uses Anthropic Claude API**

**6. mbss_check(device_name, mbss_ids)**
- Returns: Formatted MBSS verification report
- Use Case: Check compliance status of specific controls
- Parameters:
  - `device_name`: Target CPNR/Linux device
  - `mbss_ids`: Comma-separated IDs (e.g., `"1,2,9"`) or `"all"`

**7. mbss_apply(device_name, mbss_ids)**
- Returns: Formatted pre-check → remediation → post-check report
- Use Case: Apply MBSS remediation for specified controls
- Parameters:
  - `device_name`: Target device
  - `mbss_ids`: Comma-separated IDs — **`"all"` is blocked for safety**

**8. mbss_audit(device_name)**
- Returns: Full MBSS audit report (all 67 controls)
- Use Case: Run a complete CPNR compliance audit
- Parameters: `device_name`

---

### 2. **devices/** (Device Credentials Directory)

**Purpose:** One TOML file per device. Loaded at startup using Python's built-in `tomllib`. The filename stem (without `.toml`) becomes the device name used in all MCP tools. **Gitignored — credentials never enter version control.**

**File format** (e.g. `devices/my-router.toml`):
```toml
host        = "192.168.1.1"
device_type = "cisco_ios"
username    = "admin"
password    = "your_password"
description = "My Router"

# Optional — Cisco enable password:
# secret = "enable_password"

# Optional — override defaults:
# port    = 22
# timeout = 10
```

Required fields: `host`, `device_type`, `username`, `password`. Optional: `description`, `secret`, `port`, `timeout`.

**To Add a New Device:**
1. Copy `devices/example-device.toml.template` → `devices/<device-name>.toml`
2. Fill in the connection details
3. Restart the MCP server — the device is picked up automatically

---

### 3. **.env** (Environment Configuration)

**Purpose:** Store sensitive API keys. Never commit to git.

**Required Content:**
```
ANTHROPIC_API_KEY=sk-ant-your_actual_key_here
```

The server raises `ValueError` at startup if `ANTHROPIC_API_KEY` is missing.

---

### 4. **pyproject.toml** (Dependency Configuration)

**Purpose:** Define project metadata and dependencies.

**Dependencies:**
```toml
dependencies = [
    "fastmcp>=3.0.2",        # MCP protocol framework
    "netmiko>=4.6.0",        # SSH device connectivity
    "pyyaml>=6.0.3",         # YAML parsing
    "anthropic>=0.40.0",     # Anthropic Claude API
    "mcp>=1.0.0",            # MCP base library
    "python-dotenv>=1.0.0",  # .env file loading
]
```

---

### 5. **mbss/** (MBSS Security Controls Module)

**Purpose:** Contains all 67 CPNR MBSS (Minimum Baseline Security Standard) control definitions.

**Files:**
- `__init__.py` — exports `MBSS_MOP` (list of all controls) and `MBSS_BY_ID` (dict keyed by control ID)
- `mbss_mop.py` — defines all 67 controls with `verify_commands` and `remediate_commands`
- `CPNR_MBSS.htm` / `CPNR_MBSS.xlsx` — CPNR MBSS reference documents
- `cpnr_system_prompt.md` — AI system prompt with CPNR context

**Control structure:**
```python
{
    "id": 1,
    "title": "Control name",
    "applicable": True,
    "verify_commands": ["cmd1", "cmd2"],
    "remediate_commands": ["fix_cmd1"]
}
```

---

### 6. **main.py** (Standalone CLI Chat Client)

**Purpose:** Standalone terminal chat client using the Anthropic API with tool use. **Not part of the MCP server** — this is a separate utility for direct CLI interaction.

---

## Setup Instructions

### Prerequisites
- Python 3.13+
- Anthropic API key
- `uv` package manager (or pip)
- Network devices with SSH enabled

### Step 1: Get Anthropic API Key
1. Go to: https://console.anthropic.com/
2. Create a new API key
3. Copy the key (starts with `sk-ant-`)

### Step 2: Create .env File
Create file: `c:\Custom-MCP\device-mcp\.env`

```
ANTHROPIC_API_KEY=sk-ant-your_actual_key_here
```

### Step 3: Install Dependencies
```bash
cd c:\Custom-MCP\device-mcp
uv sync
```

### Step 4: Add Your Devices

Create a `.toml` file in the `devices/` folder for each device. Use the filename as the device name.

**Example: `devices/my-router.toml`**
```toml
host        = "192.168.1.1"
device_type = "cisco_ios"
username    = "admin"
password    = "your_password"
description = "My Router"
```

**Example: `devices/my-linux-server.toml`**
```toml
host        = "192.168.1.50"
device_type = "linux"
username    = "root"
password    = "your_password"
description = "Linux Server"
```

A template with all available fields is at `devices/example-device.toml.template`. These files are gitignored — credentials stay local only.

---

## How to Run

### Run MCP Server (for Claude Desktop)

```bash
cd c:\Custom-MCP\device-mcp
python device_mcp.py
```

Keep this terminal open. The MCP server listens for Claude Desktop connections.

**Configure Claude Desktop:**
1. Edit: `C:\Users\YourUsername\AppData\Roaming\Claude\claude_desktop_config.json`
2. Add:
```json
{
  "mcpServers": {
    "device-mcp": {
      "command": "python",
      "args": ["C:\\Custom-MCP\\device-mcp\\device_mcp.py"],
      "cwd": "C:\\Custom-MCP\\device-mcp"
    }
  }
}
```
3. Restart Claude Desktop
4. The 8 device tools are now available in Claude Desktop

---

## Device Interaction Methods

### Claude Desktop (Only Interface)

**Setup:**
- Configure `claude_desktop_config.json` (see above)
- Restart Claude Desktop

**Usage Examples:**
```
You: "List all available devices"
Claude: Uses list_devices() → shows ubuntu-server, rhel-cpnr

You: "Show me the hostname on rhel-cpnr"
Claude: Uses run_command() → executes "hostname" and shows output

You: "What commands can I use to check disk usage?"
Claude: Uses suggest_commands() → Claude AI recommends commands

You: "Explain this df output: ..."
Claude: Uses analyze_output() → Claude AI interprets the output

You: "Run an MBSS audit on rhel-cpnr"
Claude: Uses mbss_audit() → runs all 67 CPNR controls

You: "Check MBSS controls 1, 2, and 9 on rhel-cpnr"
Claude: Uses mbss_check("rhel-cpnr", "1,2,9")

You: "Apply remediation for MBSS controls 15 and 16"
Claude: Uses mbss_apply("rhel-cpnr", "15,16") → pre-check, fix, post-check
```

---

## MCP Tools Reference

### Standard Tools (No AI Required)

| Tool | Parameters | Returns |
|------|-----------|---------|
| `list_devices()` | None | Device names |
| `run_command()` | device_name, command | Command output |
| `get_device_info()` | device_name | Device details dict |
| `mbss_check()` | device_name, mbss_ids | Verification report |
| `mbss_apply()` | device_name, mbss_ids | Remediation report |
| `mbss_audit()` | device_name | Full 67-control report |

### AI-Powered Tools (Uses Anthropic Claude Haiku)

| Tool | Parameters | Returns |
|------|-----------|---------|
| `suggest_commands()` | device_name, intent | Suggested commands |
| `analyze_output()` | device_name, command, output | AI explanation |

---

## Configuration

### Device Inventory (`devices.yaml`)

All devices are configured in a single `devices.yaml` file at the project root.

**Supported device types (Netmiko conventions):**
```yaml
device_type: "cisco_ios"         # Cisco IOS
device_type: "cisco_xe"          # Cisco IOS XE
device_type: "cisco_xr"          # Cisco IOS XR
device_type: "cisco_nxos"        # Cisco NX-OS
device_type: "linux"             # Linux/RHEL
device_type: "arista_eos"        # Arista EOS
device_type: "juniper_junos"     # Juniper Junos
```

See [Netmiko Device Types](https://github.com/ktbyers/netmiko/blob/develop/netmiko/ssh_dispatcher.py) for the full list.

### Change AI Model

**Location:** `device_mcp.py` — find all instances of `model="claude-haiku-4-5-20251001"` and change to another Anthropic model:

```python
model="claude-haiku-4-5-20251001"   # Fast, economical (current default)
model="claude-sonnet-4-6"           # More capable, balanced cost
model="claude-opus-4-6"             # Most capable
```

---

## Troubleshooting

### Issue: "ANTHROPIC_API_KEY environment variable not set"
**Solution:** Ensure `.env` file exists with `ANTHROPIC_API_KEY=sk-ant-...`

### Issue: "Device not found"
**Solution:**
- Check the device name in `devices.yaml`
- Use `list_devices()` to see available device names
- Ensure `devices.yaml` is valid YAML

### Issue: "SSH Connection failed"
**Solution:**
- Verify device IP (`host`) is reachable: `ping <host>`
- Check `username` and `password` in `devices.yaml`
- Confirm `device_type` matches the actual device OS
- Verify SSH is enabled on the device (port 22)

### Issue: MCP server not visible in Claude Desktop
**Solution:**
- Ensure `claude_desktop_config.json` has the correct path to `device_mcp.py`
- Use absolute paths with double backslashes on Windows
- Restart Claude Desktop after config changes

---

## Summary

This Device MCP system provides:
- 8 powerful MCP tools accessible from Claude Desktop
- AI-powered command suggestions and output analysis (Anthropic Claude)
- SSH connectivity to Linux and Cisco devices via Netmiko
- Full MBSS compliance auditing and remediation (67 CPNR controls)

**Quick Start:**
1. `uv sync` — install dependencies
2. Create `.env` with your `ANTHROPIC_API_KEY`
3. Update `devices.yaml` with your devices
4. Run `python device_mcp.py`
5. Configure Claude Desktop and start managing!

---

**Last Updated:** March 25, 2026

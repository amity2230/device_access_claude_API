# Device Access — Network Operations Assistant

A standalone AI-powered CLI client for managing network devices over SSH. Uses the Anthropic Claude API for all AI work — no IDE, no Claude Desktop, no external MCP client required.

## What it does

You chat with it in the terminal. It connects to your network devices via SSH and uses Claude as the brain to:

- Run CLI commands on devices
- Analyze command output
- Suggest appropriate commands for your intent
- Perform MBSS (Minimum Baseline Security Standard) compliance checks and hardening

## Quickstart

**1. Clone the repo**

    git clone https://github.com/amity2230/device_access.git
    cd device_access

**2. Install dependencies**

    uv sync

Or with pip:

    pip install fastmcp netmiko pyyaml anthropic python-dotenv

**3. Set your Anthropic API key**

    cp .env.example .env

Edit `.env`:

    ANTHROPIC_API_KEY=your-anthropic-api-key-here

**4. Add your devices**

Edit `devices.yaml`:

    cpnr-server-01:
      host: 192.168.1.10
      device_type: linux
      username: admin
      password: yourpassword
      description: "CPNR Server 01"

**5. Run**

    python main.py

## Usage

Just type naturally. Claude will call the right tools automatically.

    You: list all devices
    You: run "show ip interface brief" on vIOS-R1
    You: check MBSS compliance for cpnr-server-01
    You: apply MBSS fixes 1,2,9 on cpnr-server-01
    You: run a full MBSS audit on cpnr-server-01

Type `quit` or `exit` to end the session.

## Available Tools

Claude automatically decides when to call these based on your request:

| Tool | What it does |
|------|--------------|
| `list_devices` | Show all devices in inventory |
| `get_device_info` | Get connection details for a device |
| `run_command` | Execute a CLI command on a device via SSH |
| `suggest_commands` | AI-suggested commands for a given intent |
| `analyze_output` | AI analysis of command output |
| `mbss_check` | Verify MBSS compliance for specific controls |
| `mbss_apply` | Apply MBSS remediation (verify → fix → verify) |
| `mbss_audit` | Full MBSS audit across all 67 controls |

## Project Structure

    device_access/
    ├── main.py              # Standalone CLI client — run this
    ├── device_mcp.py        # Tool functions (SSH, MBSS, AI helpers)
    ├── mbss/
    │   ├── mbss_mop.py      # MBSS control definitions (67 controls)
    │   ├── CPNR_MBSS.htm    # MBSS reference document
    │   ├── CPNR_MBSS.xlsx   # MBSS reference spreadsheet
    │   └── cpnr_system_prompt.md
    ├── devices.yaml         # Your device inventory
    ├── pyproject.toml       # Dependencies
    ├── .env.example         # API key template
    └── README.md

## Supported Device Types

Follows Netmiko conventions: `cisco_ios`, `cisco_nxos`, `cisco_xr`, `arista_eos`, `juniper_junos`, `linux`, and more.

## License

MIT

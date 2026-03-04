# Device MCP - Complete Project Documentation

**Version:** 1.0.0  
**Created:** March 1, 2026  
**Project Type:** Model Context Protocol (MCP) Server with Flask Web Interface  

---

## Executive Summary

**Device MCP** is a comprehensive network device management system that combines:
- A **Model Context Protocol (MCP) Server** for Claude Desktop integration
- An **AI-powered Flask Web Interface** for local device management
- **OpenAI Integration** for intelligent command suggestions and analysis
- **Cisco Device Support** with SSH connectivity via Netmiko

This system allows network operators to manage Cisco IOS devices intelligently through multiple interfaces: Claude Desktop, Web Dashboard, or Chat UI.

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
┌─────────────────────────────────────────────────────┐
│                   User Interfaces                    │
├──────────────────┬──────────────────┬───────────────┤
│  Claude Desktop  │  Web Dashboard   │  Chat UI      │
│   (MCP Server)   │  (Flask Port     │ (localhost:   │
│                  │   5000)          │   5000/chat)  │
└────────┬─────────┴────────┬─────────┴─────────┬─────┘
         │                  │                   │
         └──────────────────┴───────────────────┘
                    │
         ┌──────────▼──────────┐
         │  Device MCP Core    │
         │ - device_mcp.py     │
         │ - web_app.py        │
         └──────────┬──────────┘
                    │
         ┌──────────┴──────────┐
         │                     │
    ┌────▼─────┐         ┌────▼──────────┐
    │  Netmiko │         │   OpenAI API  │
    │  (SSH)   │         │   (GPT-4)     │
    └────┬─────┘         └───────────────┘
         │
    ┌────▼─────────────────┐
    │  Cisco IOS Devices   │
    │ - vIOS-R1            │
    │ - vIOS-R2            │
    │ - vIOS-R3            │
    └──────────────────────┘
```

### Key Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| MCP Framework | FastMCP | 3.0.2+ | Claude Desktop integration |
| SSH Library | Netmiko | 4.6.0+ | Device connectivity |
| Web Framework | Flask | 3.0.0+ | Web interface |
| AI Model | OpenAI (GPT-4) | Latest | Intelligent assistance |
| Config Format | YAML | 6.0.3+ | Device inventory |
| Environment | Python | 3.13+ | Runtime |

---

## Project Capabilities

### ✅ Device Management
- **List all devices** - View available network devices
- **Device info** - Get connection details and metadata
- **Device profiles** - Comprehensive device information collection
- **Batch operations** - Execute multiple commands

### ✅ Command Execution
- **Show commands** - Read device information (show version, interfaces, etc.)
- **Configuration** - Set device configurations
- **Direct execution** - Run any Cisco IOS command

### ✅ AI-Powered Features
- **Command suggestions** - GPT-4 suggests commands based on intent
- **Output analysis** - GPT-4 explains command outputs
- **Device understanding** - AI-powered device capability insights
- **Chat assistant** - Conversational network support

### ✅ Multiple Interfaces
- **Claude Desktop** - Chat-based using MCP protocol
- **Web Dashboard** - Visual UI for all operations
- **Chat Interface** - Claude-like chat experience

---

## Project Structure & Files

```
device-mcp/
├── device_mcp.py           # MCP Server (Main application)
├── web_app.py              # Flask Web Application
├── devices/                # Per-device configuration files (NEW)
│   ├── vIOS-R1.yaml       # Router 1 credentials and config
│   ├── vIOS-R2.yaml       # Router 2 credentials and config
│   └── vIOS-R3.yaml       # Router 3 credentials and config
├── devices.yaml            # Legacy device inventory (DEPRECATED)
├── .env                     # OpenAI API key (environment variables)
├── pyproject.toml           # Project dependencies & metadata
├── main.py                  # Placeholder entry point
├── README.md                # Project documentation
├── templates/               # Web UI templates
│   ├── index.html          # Main dashboard
│   └── chat.html           # Chat interface
├── .venv/                   # Python virtual environment
└── uv.lock                  # Dependency lock file
```

---

## File Descriptions

### 1. **device_mcp.py** (MCP Server - Core Application)

**Purpose:** Main FastMCP server that provides tools for device management

**Key Sections:**

#### Imports & Initialization (Lines 1-50)
```python
from fastmcp import FastMCP
from netmiko import ConnectHandler
from pathlib import Path
import yaml, os
from openai import OpenAI
from dotenv import load_dotenv

mcp = FastMCP("DeviceCommands")
load_dotenv()  # Load .env file

# Load per-device credentials from individual YAML files
def load_all_devices(devices_dir: str = "devices") -> dict:
    """Load all device configurations from individual YAML files"""
    devices = {}
    devices_path = Path(devices_dir)
    
    for device_file in devices_path.glob("*.yaml"):
        with open(device_file, "r") as f:
            device_config = yaml.safe_load(f)
            if device_config and "name" in device_config:
                device_name = device_config["name"]
                devices[device_name] = device_config
    
    return devices

DEVICES = load_all_devices()  # Loads from devices/*.yaml
```
- Sets up FastMCP server instance
- Loads environment variables (including OpenAI API key)
- Initializes OpenAI client
- **NEW:** Loads per-device credentials from individual YAML files in the `devices/` directory

#### Device Inventory (Per-Device)
Each device now has its own YAML file in the `devices/` directory with the following structure:
```yaml
name: vIOS-R1
host: 192.168.1.101
device_type: cisco_ios
username: admin_user
password: admin_password
secret: enable_password  # Optional
port: 22
timeout: 15
conn_timeout: 10
```
- Stores SSH credentials **per device** (not shared)
- Allows different username/password for each device
- Supports optional enable password via `secret` field

#### Available Tools (8 MCP Tools):

**1. list_devices()** (Lines 35-41)
- Returns: List of all available device names
- Use Case: See which devices are available
- No parameters required

**2. run_command(device_name, command)** (Lines 44-70)
- Returns: Command output from device
- Use Case: Execute show/config commands
- Parameters:
  - `device_name`: Device to connect to
  - `command`: Cisco command to execute
- Supports both read (show) and write (config) commands

**3. execute_config_commands(device_name, commands)** (Lines 72-109)
- Returns: Configuration confirmation
- Use Case: Batch configuration changes
- Parameters:
  - `device_name`: Target device
  - `commands`: List of config commands
- Automatically handles config mode entry/exit

**4. get_device_info(device_name)** (Lines 111-122)
- Returns: Device IP, host info as dictionary
- Use Case: Verify device connection details
- Parameters: `device_name`

**5. suggest_commands(device_name, intent)** (Lines 124-147)
- Returns: GPT-4 suggested Cisco commands
- Use Case: Get command suggestions (AI-powered)
- Parameters:
  - `device_name`: Target device
  - `intent`: What you want to accomplish
- **Uses OpenAI API**

**6. analyze_output(device_name, command, output)** (Lines 149-169)
- Returns: AI-generated explanation of output
- Use Case: Understand complex command output
- Parameters:
  - `device_name`: Device that ran command
  - `command`: Command that was executed
  - `output`: Raw output to analyze
- **Uses OpenAI API**

**7. get_device_profile(device_name)** (Lines 171-210)
- Returns: Comprehensive device info dictionary
- Use Case: Collect all device information at once
- Gathers: version, interfaces, routing, config
- Parameters: `device_name`

**8. understand_device(device_name)** (Lines 212-243)
- Returns: AI-generated device capability analysis
- Use Case: AI explains device role and status
- Parameters: `device_name`
- **Uses OpenAI API**

---

### 2. **web_app.py** (Flask Web Application)

**Purpose:** Provides REST API and web interface for device management

**Key Sections:**

#### Initialization (Lines 1-50)
```python
from flask import Flask, render_template, request, jsonify
from netmiko import ConnectHandler
from pathlib import Path
import yaml, os

# Load per-device credentials from individual YAML files
def load_all_devices(devices_dir: str = "devices") -> dict:
    """Load all device configurations from individual YAML files"""
    devices = {}
    devices_path = Path(devices_dir)
    
    for device_file in devices_path.glob("*.yaml"):
        with open(device_file, "r") as f:
            device_config = yaml.safe_load(f)
            if device_config and "name" in device_config:
                device_name = device_config["name"]
                devices[device_name] = device_config
    
    return devices

DEVICES = load_all_devices()
```
- Flask app setup
- OpenAI client initialization
- **NEW:** Device inventory loaded from individual YAML files in `devices/` directory (same as device_mcp.py)

#### Routes & Features:

**Main Dashboard** (Route: `/`)
```python
@app.route('/')
def index():
    return render_template('index.html', devices=list(DEVICES.keys()))
```
- Displays main interface with all device tools
- Shows Available devices in sidebar
- Access at: `http://localhost:5000`

**Chat Interface** (Route: `/chat`)
```python
@app.route('/chat')
def chat():
    return render_template('chat.html', devices=list(DEVICES.keys()))
```
- Claude-like chat interface
- Access at: `http://localhost:5000/chat`

**API Endpoints** (JSON responses):

1. **GET /api/devices** - Get list of devices
2. **GET /api/device-info/<device>** - Get device details
3. **POST /api/run-command** - Execute command
   - **Updated:** Uses per-device credentials from device config file
4. **POST /api/suggest-commands** - Get AI suggestions
5. **POST /api/analyze-output** - Analyze command output
6. **POST /api/chat** - Chat with AI

---

### 3. **devices/ Directory** (Per-Device Configuration Files)

**Purpose:** Store individual credentials and configuration for each device

**Structure:**
```
devices/
├── vIOS-R1.yaml
├── vIOS-R2.yaml
└── vIOS-R3.yaml
```

**File Format:** Each device file contains complete connection credentials:
```yaml
name: vIOS-R1                           # Device identifier
host: 192.168.1.101                    # IP address
device_type: cisco_ios                 # Device OS type
username: admin1                        # SSH username (device-specific)
password: password123                   # SSH password (device-specific)
secret: cisco                          # Enable password (optional)
port: 22                               # SSH port
timeout: 15                            # Command timeout (seconds)
conn_timeout: 10                       # Connection timeout (seconds)
```

**Advantages of Per-Device Credentials:**
- ✅ Each device can have different username/password
- ✅ Support for multiple SSH ports per device
- ✅ Device-specific timeouts for slow/fast networks
- ✅ Optional enable passwords (secret field)
- ✅ Easy to manage at scale
- ✅ No shared credentials across devices

**To Add New Device:**
1. Create a new file: `devices/NEW_DEVICE_NAME.yaml`
2. Add device configuration with unique credentials:
```yaml
name: vIOS-R4
host: 192.168.1.104
device_type: cisco_ios
username: admin_user
password: unique_password
secret: enable_pass
port: 22
timeout: 15
conn_timeout: 10
```
3. Restart the application - device automatically loads!

---

### 4. **devices.yaml** (Legacy - DEPRECATED)

**Status:** No longer used in favor of individual per-device configuration files

**Note:** Kept for reference only. All device management now uses the `devices/` directory structure with per-device credential files

**Previous Format (For Reference):**
```yaml
vIOS-R1:
  host: 192.168.1.101

vIOS-R2:
  host: 192.168.1.102

vIOS-R3:
  host: 192.168.1.103
```

---

### 4. **.env** (Environment Configuration)

**Purpose:** Store sensitive API keys

**Content:**
```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx...
```

**Why This Matters:**
- Stores your OpenAI API key securely
- Automatically loaded by `load_dotenv()`
- Never commit to git (added to .gitignore)

**To Set Up:**
1. Get OpenAI API key from: https://platform.openai.com/api-keys
2. Add to `.env`:
```
OPENAI_API_KEY=your_actual_key_here
```

---

### 5. **pyproject.toml** (Dependency Configuration)

**Purpose:** Define project metadata and dependencies

**Key Sections:**

**Project Info:**
```toml
[project]
name = "device-mcp"
version = "0.1.0"
requires-python = ">=3.13"
```

**Dependencies:**
```toml
dependencies = [
    "fastmcp>=3.0.2",      # MCP protocol
    "netmiko>=4.6.0",      # SSH to devices
    "pyyaml>=6.0.3",       # YAML parsing
    "openai>=1.0.0",       # OpenAI API
    "python-dotenv>=1.0.0",  # .env loading
    "flask>=3.0.0",        # Web framework
]
```

---

### 6. **templates/index.html** (Main Dashboard)

**Purpose:** Web interface for device management

**Key Sections:**

- **Header** - Title and Chat link
- **Cards** (5 main sections):
  1. **Available Devices** - List all devices
  2. **Device Information** - Get device details
  3. **Run Command** - Execute commands
  4. **AI Suggestions** - Get command recommendations
  5. **Output Analysis** - Analyze command results

**Features:**
- Real-time device listing
- Form-based command execution
- Loading indicators
- Color-coded responses (success/error)
- Responsive design

---

### 7. **templates/chat.html** (Chat Interface)

**Purpose:** Claude-like chat experience

**Key Sections:**

- **Sidebar** - Device selection and context
- **Chat Area** - Message display
- **Input Area** - User message entry
- **Device Context** - Shows selected device details

**Features:**
- Real-time messaging
- Device context awareness
- Typing indicators
- Message history
- Professional UI

---

## Setup Instructions

### Prerequisites
- Python 3.13+
- OpenAI API key
- Virtual environment tool (venv or uv)
- Windows PowerShell or compatible terminal
- Cisco IOS devices with SSH enabled

### Step 1: Get OpenAI API Key
1. Go to: https://platform.openai.com/api-keys
2. Create new API key
3. Copy the key (starts with `sk-proj-`)

### Step 2: Create .env File
Create file: `c:\Custom-MCP\device-mcp\.env`

Content:
```
OPENAI_API_KEY=sk-proj-your_actual_key_here
```

### Step 3: Install Dependencies
```powershell
cd c:\Custom-MCP\device-mcp
uv sync
```

### Step 4: Create Per-Device Configuration Files
Create the `devices/` directory and add individual credential files for each device.

**Example: Create `devices/vIOS-R1.yaml`**
```yaml
name: vIOS-R1
host: 192.168.1.101
device_type: cisco_ios
username: admin1
password: password123
secret: cisco
port: 22
timeout: 15
conn_timeout: 10
```

**Create additional files for each device:**
- `devices/vIOS-R2.yaml` (with different credentials if needed)
- `devices/vIOS-R3.yaml` (with different credentials if needed)
- etc.

**Key Points:**
- Each device file must have a unique `name` field
- `username` and `password` can differ per device (no shared credentials)
- `secret` field is optional (for enable password)
- `device_type` typically `cisco_ios` but can be `cisco_xe`, `cisco_xr`, etc.
- Files are automatically loaded when application starts

### Step 5: Verify Device Configuration
Check that all device files are present:
```powershell
ls c:\Custom-MCP\device-mcp\devices\
```

---

## How to Run

### Option 1: Run MCP Server (for Claude Desktop)

**Terminal 1 - Start MCP Server:**
```powershell
cd c:\Custom-MCP\device-mcp
& .\.venv\Scripts\Activate.ps1
python device_mcp.py
```

Keep this terminal open. MCP server is now listening for Claude Desktop.

**Then Configure Claude Desktop:**
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
4. Start chatting with device tools!

---

### Option 2: Run Web Interface (Recommended for Daily Use)

```powershell
cd c:\Custom-MCP\device-mcp
& .\.venv\Scripts\Activate.ps1
python web_app.py
```

**Output:**
```
WARNING: This is a development server. Do not use in production.
Running on http://127.0.0.1:5000
```

**Access:**
- Main Dashboard: http://localhost:5000
- Chat UI: http://localhost:5000/chat

---

### Option 3: Run Both (Advanced)

**Terminal 1:**
```powershell
cd c:\Custom-MCP\device-mcp
& .\.venv\Scripts\Activate.ps1
python device_mcp.py
```

**Terminal 2:**
```powershell
cd c:\Custom-MCP\device-mcp
& .\.venv\Scripts\Activate.ps1
python web_app.py
```

Both servers run simultaneously.

---

## Device Interaction Methods

### Method 1: Claude Desktop (Chat-Based)

**Setup:**
- Configure `claude_desktop_config.json` (see above)
- Restart Claude Desktop

**Usage:**
```
You: "List all available devices"
Claude: Shows list using list_devices() tool

You: "Show me the version on vIOS-R1"
Claude: Executes run_command() and displays output

You: "What commands can I use to check BGP?"
Claude: Uses suggest_commands() for AI recommendations

You: "Explain this BGP output: ..."
Claude: Uses analyze_output() for AI interpretation
```

**Advantages:**
- Natural conversation
- Multi-turn interactions
- Context awareness
- Can combine multiple tools

---

### Method 2: Web Dashboard (Visual UI)

**Access:** http://localhost:5000

**Features:**

1. **Available Devices Card**
   - Click "Refresh" to view all devices
   - Displayed as clickable badges

2. **Device Information Card**
   - Select device
   - Click "Get Device Info"
   - View JSON details

3. **Run Command Card**
   - Select device
   - Enter command (e.g., "show version")
   - Click "Execute"
   - View output

4. **AI Suggestions Card**
   - Select device
   - Describe intent: "Show all interfaces"
   - Click "Get Suggestions"
   - View AI-recommended commands

5. **AI Analysis Card**
   - Select device
   - Enter original command
   - Paste output
   - Click "Analyze"
   - View AI interpretation

---

### Method 3: Chat Interface (Claude-Like)

**Access:** http://localhost:5000/chat

**Features:**
- Real-time conversation
- Device context sidebar
- Message history
- Loading indicators
- Professional UI

**Example:**
```
User: "Hello, tell me about vIOS-R1"
AI: [Analyzes device, shows capabilities]

User: "What OSPF settings does it have?"
AI: [Extracts and explains OSPF config]

User: "Show interfaces brief"
AI: [Executes command and displays]
```

---

### Method 4: Direct Python Scripts

For automation and scripting:

```python
from device_mcp import (
    list_devices,
    run_command,
    suggest_commands,
    analyze_output,
    get_device_profile,
    understand_device
)

# Get all devices
devices = list_devices()
print(devices)

# Run command
output = run_command("vIOS-R1", "show ip route")
print(output)

# Get suggestions
suggestion = suggest_commands("vIOS-R1", "show BGP routes")
print(suggestion)

# Analyze output
analysis = analyze_output("vIOS-R1", "show version", output)
print(analysis)
```

---

### Method 5: REST API Calls

Using curl, Postman, or Python requests:

```bash
# Get devices
curl http://localhost:5000/api/devices

# Run command
curl -X POST http://localhost:5000/api/run-command \
  -H "Content-Type: application/json" \
  -d '{"device":"vIOS-R1","command":"show version"}'

# Get suggestions
curl -X POST http://localhost:5000/api/suggest-commands \
  -H "Content-Type: application/json" \
  -d '{"device":"vIOS-R1","intent":"check interfaces"}'
```

---

## MCP Tools Reference

### Standard Tools (No AI Required)

| Tool | Parameters | Returns | Cost |
|------|-----------|---------|------|
| `list_devices()` | None | Device names | Free |
| `run_command()` | device, command | Command output | Free |
| `get_device_info()` | device | Device details | Free |
| `execute_config_commands()` | device, commands | Config confirmation | Free |
| `get_device_profile()` | device | Comprehensive info | Free |

### AI-Powered Tools (Uses OpenAI GPT-4)

| Tool | Parameters | Returns | Cost |
|------|-----------|---------|------|
| `suggest_commands()` | device, intent | Suggested commands | ~$0.03/1K tokens |
| `analyze_output()` | device, command, output | Explanation | ~$0.03/1K tokens |
| `understand_device()` | device | Device analysis | ~$0.03/1K tokens |

---

## Configuration

### Per-Device SSH Credentials (NEW)

**Location:** Individual files in `devices/` directory

Each device has its own YAML file with credentials:

**Example: `devices/vIOS-R1.yaml`**
```yaml
name: vIOS-R1
host: 192.168.1.101
device_type: cisco_ios
username: admin1
password: password123
secret: cisco
port: 22
timeout: 15
conn_timeout: 10
```

**Security Best Practices:**
- ✅ Different credentials per device allowed
- ✅ Store sensitive passwords in `.env` and reference them
- ✅ Use environment variables in device YAML files:

**Advanced: Use Environment Variables in Device Files**
```yaml
name: vIOS-R1
host: 192.168.1.101
device_type: cisco_ios
username: ${DEVICE_USER_R1}      # Reference from .env
password: ${DEVICE_PASS_R1}      # Reference from .env
secret: ${DEVICE_SECRET_R1}      # Reference from .env
port: 22
timeout: 15
conn_timeout: 10
```

Then add to `.env`:
```
DEVICE_USER_R1=admin1
DEVICE_PASS_R1=password123
DEVICE_SECRET_R1=cisco
```

**Note:** Current version uses direct values. For production use, implement environment variable substitution in `load_all_devices()` function.

---

### Device Type Support

Current: **Cisco IOS** (primary)

To support other device types, update `device_type` in device YAML files:

```yaml
# Cisco IOS (standard)
device_type: "cisco_ios"

# Cisco IOS XE
device_type: "cisco_xe"

# Cisco IOS XR
device_type: "cisco_xr"

# Arista EOS
device_type: "arista_eos"

# Juniper Junos
device_type: "juniper_junos"

# Palo Alto Networks
device_type: "paloaltonetworks_panos"

# Dell Force10
device_type: "dell_force10"
```

See [Netmiko Device Types](https://github.com/ktbyers/netmiko/blob/develop/netmiko/ssh_dispatcher.py) for full list.

---

### Modify OpenAI Model

**Location:** `device_mcp.py` and `web_app.py`

Find all instances of:
```python
model="gpt-4"
```

Change to:
```python
model="gpt-4-turbo"  # Faster, cheaper alternative
# or
model="gpt-3.5-turbo"  # Most economical option
```

---

## Troubleshooting

### Issue: "API Key not found"
**Solution:** Ensure .env file exists with valid OPENAI_API_KEY

### Issue: "Device not found"
**Solution:** 
- Ensure device YAML file exists in `devices/` directory
- Check that `name:` field in device YAML matches device name used in commands
- Verify file is properly formatted YAML

### Issue: "SSH Connection failed"
**Solution:** 
- Verify device IP is correct in device YAML file
- Check username/password in the specific device YAML file (not shared)
- Ensure device is reachable (ping test)
- Verify SSH port (default 22) matches device SSH configuration
- Confirm `device_type` is correct for your device (cisco_ios, cisco_xe, etc.)

Example checking device configuration:
```powershell
# View device config
cat devices/vIOS-R1.yaml

# Test connectivity
ping 192.168.1.101  # Replace with your device IP
```

### Issue: "Web app won't start"
**Solution:** 
- Port 5000 might be in use
- Edit `web_app.py` last line: `port=5001` (change port)
- Ensure virtual environment is activated
- Check that devices directory exists and has YAML files

### Issue: "Commands not executing on device"
**Solution:**
- Verify the device credentials (username/password) in the device YAML file
- Check that the device allows SSH access (not just Telnet)
- Ensure enable password (secret) is correct if running privileged commands
- Check command syntax for the specific IOS version

---

## Summary

This Device MCP system provides:
✅ Multiple device access methods (Claude Desktop, Web Dashboard, Chat UI, MCP, API)
✅ 8 powerful tools for device management
✅ Per-device credential management (no shared passwords)
✅ AI-powered command suggestions & analysis
✅ Enterprise-grade SSH connectivity
✅ Scalable to many devices with individual credentials

**Next Steps:**
1. Install dependencies: `uv sync`
2. Add OpenAI key to `.env`
3. Update `devices.yaml` with your devices
4. Update SSH credentials
5. Run preferred interface
6. Start managing!

---

**For Questions or Updates:** Refer to individual file documentation above.

**Last Updated:** March 1, 2026

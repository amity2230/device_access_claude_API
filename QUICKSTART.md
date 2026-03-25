# Quickstart Guide

Get the Network Operations Assistant running in 5 minutes.

---

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended) or pip
- An [Anthropic API key](https://console.anthropic.com/)
- SSH access to your network devices

---

## Step 1 — Clone the repo

```bash
git clone https://github.com/amity2230/device_access.git
cd device_access
```

---

## Step 2 — Install dependencies

**Using uv (recommended):**

```bash
uv sync
```

**Using pip:**

```bash
pip install fastmcp netmiko pyyaml anthropic python-dotenv
```

---

## Step 3 — Set your Anthropic API key

```bash
cp .env.example .env
```

Open `.env` and add your key:

```
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

Get your API key at: https://console.anthropic.com/

---

## Step 4 — Add your devices

Open `devices.yaml` and add your devices:

```yaml
my-router:
  host: 192.168.1.1
  device_type: cisco_ios
  username: admin
  password: yourpassword
  description: "My Cisco Router"

my-linux-server:
  host: 192.168.1.10
  device_type: linux
  username: root
  password: yourpassword
  description: "My Linux Server"
```

**Supported device types:** `cisco_ios`, `cisco_nxos`, `cisco_xr`, `arista_eos`, `juniper_junos`, `linux`

---

## Step 5 — Run

```bash
python main.py
```

You should see:

```
==================================================
  Network Operations Assistant
==================================================
Ask me anything about your network devices.
Type 'quit' or 'exit' to end the session.

You:
```

---

## Example Prompts

```
You: list all devices
You: show me the interfaces on my-router
You: run "show version" on my-router
You: check MBSS compliance for my-linux-server
You: run a full MBSS audit on my-linux-server
You: apply MBSS fixes 1,2,9 on my-linux-server
You: analyze the routing table on my-router
```

---

## Troubleshooting

**`ANTHROPIC_API_KEY environment variable not set`**
→ Make sure your `.env` file exists and contains a valid key.

**`Device 'xyz' not found`**
→ Run `list all devices` first to see exact device names from `devices.yaml`.

**SSH connection errors**
→ Verify the device `host`, `username`, and `password` in `devices.yaml`.
→ Make sure the device is reachable and SSH is enabled.

**`ModuleNotFoundError`**
→ Run `uv sync` or `pip install -r requirements` again to ensure all dependencies are installed.

---

## Project Files

| File | Purpose |
|------|---------|
| `main.py` | The client — run this |
| `device_mcp.py` | Tool functions (SSH, MBSS, AI) |
| `mbss/` | MBSS control definitions, reference docs, system prompt |
| `devices.yaml` | Your device inventory |
| `.env` | Your API key (never commit this) |

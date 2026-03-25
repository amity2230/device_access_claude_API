
#!/usr/bin/env python3
from fastmcp import FastMCP
from netmiko import ConnectHandler
import tomllib
import os
import anthropic
from dotenv import load_dotenv
from pathlib import Path
from mbss import MBSS_MOP, MBSS_BY_ID

# Load environment variables from .env file
load_dotenv()

#Initilize MCP server
mcp = FastMCP("DeviceCommands")

# Anthropic client initialization
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY environment variable not set")
claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


# Load device inventory from devices/*.toml
# Each .toml file = one device; the filename stem is the device name.
def load_inventory(devices_dir: str = "devices") -> dict:
    devices = {}
    for toml_file in sorted(Path(devices_dir).glob("*.toml")):
        with open(toml_file, "rb") as f:
            devices[toml_file.stem] = tomllib.load(f)
    return devices

DEVICES = load_inventory()

@mcp.tool()
def list_devices() -> str:
    """List all available network devices in the inventory.
    
    Returns:
        A newline-separated list of device names available for connection.
        Use device names with run_command() or get_device_info().
    """
    return "\n".join(DEVICES.keys())


@mcp.tool()
def run_command(device_name: str, command: str) -> str:
    """Execute a CLI command on a Cisco IOS device via SSH connection.
    
    Supported commands: show interfaces, show ip route, show bgp, show version,
    show running-config, and other Cisco IOS show commands.
    
    Args:
        device_name: Exact name of the device from the inventory (e.g., ubuntu-server).
                    Use list_devices() to see available options.
        command: CLI command to execute on the device (e.g., 'hostname', 'ip a', 'df -h').
    
    Returns:
        Command output from the device, or error message if device not found or connection fails.
    """
    if device_name not in DEVICES:
        return f"Error: Device {device_name} not found"
    
    device_info = DEVICES[device_name]
    connection_params = {
        "host": device_info["host"],
        "device_type": device_info["device_type"],
        "username": device_info["username"],
        "password": device_info["password"],
    }
    
    try:
        with ConnectHandler(**connection_params) as conn:
            output = conn.send_command(command)
            return output
    except Exception as e:
        return f"Error: {str(e)}"
    
@mcp.tool()
def get_device_info(device_name: str) -> dict:
    """Retrieve connection details and metadata for a specific device.
    
    Args:
        device_name: Exact name of the device (e.g., vIOS-R1). Use list_devices()
                    to see available device names.
    
    Returns:
        Dictionary containing device connection information (host IP, device type, etc.).
        Useful for validation before running commands or for planning network operations.
    """
    if device_name not in DEVICES:
        return {"error": f"Device {device_name} not found. Use list_devices() to see available devices."}
    return DEVICES[device_name]

@mcp.tool()
def suggest_commands(device_name: str, intent: str) -> str:
    """Use AI to suggest appropriate Cisco commands for a given intent.
    
    Args:
        device_name: Name of the target device (e.g., vIOS-R1)
        intent: What you want to accomplish (e.g., 'show all interface statuses')
    
    Returns:
        Suggested Cisco IOS command(s) to accomplish the intent.
    """
    if device_name not in DEVICES:
        return f"Error: Device {device_name} not found"
    
    try:
        response = claude_client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            system="You are a Cisco IOS network expert. Suggest appropriate show commands for the user's intent. Return only the command(s), no explanation.",
            messages=[
                {"role": "user", "content": f"For {device_name}: {intent}"}
            ],
        )
        return response.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def analyze_output(device_name: str, command: str, output: str) -> str:
    """Use AI to analyze and explain command output from a device.
    
    Args:
        device_name: Name of the device that ran the command
        command: The command that was executed (e.g., 'show ip route')
        output: The raw output from the device
    
    Returns:
        AI-generated analysis and insights about the command output.
    """
    try:
        response = claude_client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system="You are a Cisco IOS network expert. Analyze command output and provide clear insights.",
            messages=[
                {"role": "user", "content": f"Device: {device_name}\nCommand: {command}\nOutput:\n{output}\n\nProvide a brief analysis."},
            ],
        )
        return response.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"
# ---------------------------------------------------------------------------
# MBSS helpers
# ---------------------------------------------------------------------------

def _parse_mbss_ids(mbss_ids: str) -> list:
    """Return list of MBSS item dicts for a comma-separated ID string or 'all'."""
    if mbss_ids.strip().lower() == "all":
        return MBSS_MOP
    ids = []
    for part in mbss_ids.split(","):
        part = part.strip()
        if part.isdigit():
            ids.append(int(part))
    return [MBSS_BY_ID[i] for i in ids if i in MBSS_BY_ID]


def _ssh_run_commands(device_info: dict, commands: list) -> tuple:
    """
    Open one SSH connection and run all commands sequentially.
    Returns (hostname, [(cmd, output), ...])
    """
    params = {
        "host": device_info["host"],
        "device_type": device_info["device_type"],
        "username": device_info["username"],
        "password": device_info["password"],
    }
    results = []
    hostname = device_info.get("host", "unknown")
    try:
        with ConnectHandler(**params) as conn:
            hostname = conn.send_command("hostname", read_timeout=10).strip()
            for cmd in commands:
                try:
                    out = conn.send_command(cmd, read_timeout=60)
                    results.append((cmd, out))
                except Exception as e:
                    results.append((cmd, f"Error: {e}"))
    except Exception as e:
        for cmd in commands:
            results.append((cmd, f"Connection error: {e}"))
    return hostname, results


def _format_item_output(hostname: str, item: dict, cmd_results: list) -> str:
    """Format one MBSS item's results in the standard report style."""
    na = " [NOT APPLICABLE]" if not item["applicable"] else ""
    lines = [f"\nMBSS#{item['id']}: {item['title']}{na}"]
    for cmd, out in cmd_results:
        lines.append(f"[root@{hostname} ~]# {cmd}")
        lines.append(out if out else "(no output)")
        lines.append(f"[root@{hostname} ~]#")
    lines.append("")
    lines.append("-" * 25)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# MBSS MCP tools
# ---------------------------------------------------------------------------

@mcp.tool()
def mbss_check(device_name: str, mbss_ids: str = "all") -> str:
    """Verify compliance status of MBSS controls on a CPNR/Linux device.

    Runs the verification commands for the specified controls and returns
    formatted output following the CPNR MBSS MOP standard.

    Args:
        device_name: Device name from inventory (use list_devices() to see options).
        mbss_ids: Comma-separated MBSS IDs to check, e.g. "1,2,9,10".
                  Use "all" to check every applicable control.

    Returns:
        Formatted verification output for each control, ready for audit reporting.
    """
    if device_name not in DEVICES:
        return f"Error: Device '{device_name}' not found. Use list_devices() to see options."

    items = _parse_mbss_ids(mbss_ids)
    if not items:
        return "Error: No valid MBSS IDs found. Provide comma-separated numbers or 'all'."

    device_info = DEVICES[device_name]

    # Collect all verify commands in order, tracking counts per item
    all_cmds = []
    counts = []
    for item in items:
        all_cmds.extend(item["verify_commands"])
        counts.append(len(item["verify_commands"]))

    hostname, results = _ssh_run_commands(device_info, all_cmds)

    output_parts = [f"=== MBSS Verification Report — {device_name} ({hostname}) ===\n"]
    idx = 0
    for item, count in zip(items, counts):
        item_results = results[idx: idx + count]
        idx += count
        output_parts.append(_format_item_output(hostname, item, item_results))

    return "\n".join(output_parts)


@mcp.tool()
def mbss_apply(device_name: str, mbss_ids: str) -> str:
    """Apply MBSS remediation for specified controls: verify → remediate → verify.

    For each control the tool will:
      1. Run verification commands (PRE-CHECK)
      2. Apply remediation commands if defined
      3. Re-run verification commands (POST-CHECK) to confirm the fix

    Args:
        device_name: Device name from inventory.
        mbss_ids: Comma-separated MBSS IDs to apply, e.g. "1,2,15,16".
                  Do NOT pass "all" — always specify explicit IDs to avoid
                  unintended changes (e.g. dnf update, sshd restart).

    Returns:
        Formatted output showing pre-state, remediation applied, and post-state.
    """
    if device_name not in DEVICES:
        return f"Error: Device '{device_name}' not found."

    if mbss_ids.strip().lower() == "all":
        return (
            "Safety check: 'all' is not allowed for mbss_apply. "
            "Specify explicit MBSS IDs (e.g. '1,2,15') to avoid unintended changes."
        )

    items = _parse_mbss_ids(mbss_ids)
    if not items:
        return "Error: No valid MBSS IDs found."

    device_info = DEVICES[device_name]

    # Build one flat command list: [pre_verify, remediate, post_verify] per item
    all_cmds = []
    plan = []  # (n_verify, n_remediate) per item
    for item in items:
        nv = len(item["verify_commands"])
        nr = len(item["remediate_commands"])
        all_cmds.extend(item["verify_commands"])
        all_cmds.extend(item["remediate_commands"])
        all_cmds.extend(item["verify_commands"])   # post-verify
        plan.append((nv, nr))

    hostname, results = _ssh_run_commands(device_info, all_cmds)

    output_parts = [f"=== MBSS Remediation Report — {device_name} ({hostname}) ===\n"]
    idx = 0
    for item, (nv, nr) in zip(items, plan):
        na = " [NOT APPLICABLE]" if not item["applicable"] else ""
        output_parts.append(f"\nMBSS#{item['id']}: {item['title']}{na}")

        if not item["applicable"]:
            output_parts.append("  Skipped — not applicable to this CPNR deployment.")
            output_parts.append("-" * 25)
            idx += nv + nr + nv
            continue

        pre  = results[idx:         idx + nv]
        rem  = results[idx + nv:    idx + nv + nr]
        post = results[idx + nv + nr: idx + nv + nr + nv]
        idx += nv + nr + nv

        output_parts.append("=== PRE-CHECK ===")
        for cmd, out in pre:
            output_parts.append(f"[root@{hostname} ~]# {cmd}")
            output_parts.append(out if out else "(no output)")
            output_parts.append(f"[root@{hostname} ~]#")

        if rem:
            output_parts.append("\n=== APPLYING REMEDIATION ===")
            for cmd, out in rem:
                output_parts.append(f"[root@{hostname} ~]# {cmd}")
                output_parts.append(out if out else "(no output)")
                output_parts.append(f"[root@{hostname} ~]#")

            output_parts.append("\n=== POST-CHECK ===")
            for cmd, out in post:
                output_parts.append(f"[root@{hostname} ~]# {cmd}")
                output_parts.append(out if out else "(no output)")
                output_parts.append(f"[root@{hostname} ~]#")
        else:
            output_parts.append(
                "  No remediation commands defined "
                "(already compliant, managed via ViPAM, or manual action required)."
            )

        output_parts.append("")
        output_parts.append("-" * 25)

    return "\n".join(output_parts)


@mcp.tool()
def mbss_audit(device_name: str) -> str:
    """Run a full MBSS audit across all 67 controls on a CPNR device.

    Executes every applicable verification command and returns a complete
    compliance report in the standard CPNR MBSS MOP output format.

    Args:
        device_name: Device name from inventory.

    Returns:
        Full MBSS audit report with verification output for all 67 controls.
    """
    return mbss_check(device_name, "all")


if __name__ == "__main__":
    mcp.run()









#!/usr/bin/env python3
from fastmcp import FastMCP
from netmiko import ConnectHandler
import yaml
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

#Initilize MCP server
mcp = FastMCP("DeviceCommands")

# OpenAI client initialization
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set")
openai_client = OpenAI(api_key=OPENAI_API_KEY)


# Load device inventory
def load_inventory(path: str = "devices.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

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
        device_name: Exact name of the device from the inventory (e.g., vIOS-R1, vIOS-R2, vIOS-R3).
                    Use list_devices() to see available options.
        command: Cisco IOS show command to execute (e.g., 'show ip interface brief',
                'show version', 'show running-config'). Commands should be read-only show commands.
    
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
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a Cisco IOS network expert. Suggest appropriate show commands for the user's intent. Return only the command(s), no explanation."},
                {"role": "user", "content": f"For {device_name}: {intent}"}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
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
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a Cisco IOS network expert. Analyze command output and provide clear insights."},
                {"role": "user", "content": f"Device: {device_name}\nCommand: {command}\nOutput:\n{output}\n\nProvide a brief analysis."},
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"
if __name__ == "__main__":
    mcp.run()








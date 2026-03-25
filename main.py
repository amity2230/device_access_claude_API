#!/usr/bin/env python3
import json
from device_mcp import (
    list_devices,
    run_command,
    get_device_info,
    suggest_commands,
    analyze_output,
    mbss_check,
    mbss_apply,
    mbss_audit,
    claude_client,
)

SYSTEM_PROMPT = """You are a network operations and security hardening assistant for Cisco Prime Network Registrar (CPNR) running on RHEL/AlmaLinux 9.

You have access to tools that let you:
- List devices and get device info
- Run CLI commands on devices via SSH
- Suggest commands and analyze their output
- Perform MBSS (Minimum Baseline Security Standard) compliance checks and apply hardening

MBSS Workflow:
1. Use mbss_check(device_name, mbss_ids) to verify current compliance of specific controls.
2. Use mbss_apply(device_name, mbss_ids) to apply remediation: it verifies, fixes, then verifies again.
3. Use mbss_audit(device_name) for a full audit of all 67 MBSS controls.

Always prefer running actual commands over guessing. For MBSS work:
- First check (mbss_check) before applying (mbss_apply).
- Never pass "all" to mbss_apply — always specify explicit IDs.
- Some controls are ViPAM-managed or Not Applicable; report them but do not attempt to fix.

Output format follows the CPNR MBSS MOP standard with PRE-CHECK / REMEDIATION / POST-CHECK sections."""

TOOLS = [
    {
        "name": "list_devices",
        "description": "List all available network devices in the inventory.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "run_command",
        "description": "Execute a CLI command on a network device via SSH. Use for show commands like 'show ip interface brief', 'show version', etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "device_name": {
                    "type": "string",
                    "description": "Exact device name from inventory (e.g., vIOS-R1). Use list_devices to see options.",
                },
                "command": {
                    "type": "string",
                    "description": "CLI command to execute (e.g., 'show ip interface brief').",
                },
            },
            "required": ["device_name", "command"],
        },
    },
    {
        "name": "get_device_info",
        "description": "Get connection details for a specific device (host IP, device type, description).",
        "input_schema": {
            "type": "object",
            "properties": {
                "device_name": {
                    "type": "string",
                    "description": "Exact device name from inventory.",
                },
            },
            "required": ["device_name"],
        },
    },
    {
        "name": "suggest_commands",
        "description": "Use AI to suggest appropriate CLI commands for a given intent.",
        "input_schema": {
            "type": "object",
            "properties": {
                "device_name": {
                    "type": "string",
                    "description": "Target device name.",
                },
                "intent": {
                    "type": "string",
                    "description": "What you want to accomplish (e.g., 'check all interface statuses').",
                },
            },
            "required": ["device_name", "intent"],
        },
    },
    {
        "name": "analyze_output",
        "description": "Use AI to analyze and explain raw command output from a device.",
        "input_schema": {
            "type": "object",
            "properties": {
                "device_name": {
                    "type": "string",
                    "description": "Device that produced the output.",
                },
                "command": {
                    "type": "string",
                    "description": "The command that was executed.",
                },
                "output": {
                    "type": "string",
                    "description": "The raw command output to analyze.",
                },
            },
            "required": ["device_name", "command", "output"],
        },
    },
    {
        "name": "mbss_check",
        "description": "Verify compliance status of MBSS controls on a CPNR/Linux device. Runs verification commands and returns formatted audit output.",
        "input_schema": {
            "type": "object",
            "properties": {
                "device_name": {
                    "type": "string",
                    "description": "Device name from inventory.",
                },
                "mbss_ids": {
                    "type": "string",
                    "description": "Comma-separated MBSS IDs to check (e.g. '1,2,9,10') or 'all' for every control.",
                },
            },
            "required": ["device_name"],
        },
    },
    {
        "name": "mbss_apply",
        "description": "Apply MBSS remediation for specified controls: verify → remediate → verify. Always specify explicit IDs.",
        "input_schema": {
            "type": "object",
            "properties": {
                "device_name": {
                    "type": "string",
                    "description": "Device name from inventory.",
                },
                "mbss_ids": {
                    "type": "string",
                    "description": "Comma-separated MBSS IDs to apply (e.g. '1,2,15,16'). Do not use 'all'.",
                },
            },
            "required": ["device_name", "mbss_ids"],
        },
    },
    {
        "name": "mbss_audit",
        "description": "Run a full MBSS audit across all 67 controls on a CPNR device and return a complete compliance report.",
        "input_schema": {
            "type": "object",
            "properties": {
                "device_name": {
                    "type": "string",
                    "description": "Device name from inventory.",
                },
            },
            "required": ["device_name"],
        },
    },
]

TOOL_DISPATCH = {
    "list_devices": list_devices,
    "run_command": run_command,
    "get_device_info": get_device_info,
    "suggest_commands": suggest_commands,
    "analyze_output": analyze_output,
    "mbss_check": mbss_check,
    "mbss_apply": mbss_apply,
    "mbss_audit": mbss_audit,
}


def execute_tool(name: str, arguments: dict) -> str:
    func = TOOL_DISPATCH.get(name)
    if func is None:
        return f"Error: Unknown tool '{name}'"
    try:
        result = func(**arguments)
        if not isinstance(result, str):
            return json.dumps(result, indent=2)
        return result
    except Exception as e:
        return f"Error executing {name}: {e}"


def chat(messages: list[dict]) -> None:
    while True:
        response = claude_client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        # Collect assistant content blocks
        assistant_content = response.content
        messages.append({"role": "assistant", "content": assistant_content})

        if response.stop_reason == "end_turn":
            for block in assistant_content:
                if hasattr(block, "text"):
                    print(f"\nAssistant: {block.text}\n")
            return

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in assistant_content:
                if block.type == "tool_use":
                    print(f"  [Calling {block.name}({block.input})...]")
                    result = execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
            messages.append({"role": "user", "content": tool_results})
        else:
            # Unexpected stop reason — surface any text and exit
            for block in assistant_content:
                if hasattr(block, "text"):
                    print(f"\nAssistant: {block.text}\n")
            return


def main():
    print("=" * 50)
    print("  Network Operations Assistant")
    print("=" * 50)
    print("Ask me anything about your network devices.")
    print("Type 'quit' or 'exit' to end the session.\n")

    messages = []

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("Goodbye!")
            break

        messages.append({"role": "user", "content": user_input})
        chat(messages)


if __name__ == "__main__":
    main()

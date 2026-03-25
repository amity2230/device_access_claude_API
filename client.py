#!/usr/bin/env python3
"""
Terminal-based MCP client for device management.
Uses Claude Opus 4.6 as the AI brain + device_mcp.py as the MCP server.

Usage:
    python client.py
"""

import asyncio
import os
from dotenv import load_dotenv
import anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not set in .env")

claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You are a network device management assistant with access to tools
to manage network devices including RHEL Linux servers and Cisco network devices.

Use the available MCP tools to help the user interact with their devices.
Be concise, accurate, and always confirm actions before making changes."""


async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["device_mcp.py"],
        cwd=os.path.dirname(os.path.abspath(__file__)),
        env={**os.environ, "ANTHROPIC_API_KEY": ANTHROPIC_API_KEY},
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Fetch tools from MCP server
            tools_result = await session.list_tools()
            tools = [
                {
                    "name": t.name,
                    "description": t.description or "",
                    "input_schema": t.inputSchema,
                }
                for t in tools_result.tools
            ]

            print("\n" + "=" * 60)
            print("   Device MCP Terminal Client")
            print("   Powered by Claude Opus 4.6")
            print("=" * 60)
            print(f"   MCP Server  : device_mcp.py")
            print(f"   Tools loaded: {len(tools)}")
            for t in tools:
                print(f"     - {t['name']}")
            print("   Type 'exit' or 'quit' to leave")
            print("=" * 60 + "\n")

            messages = []

            while True:
                # Get user input
                try:
                    user_input = input("You: ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\nExiting...")
                    break

                if not user_input:
                    continue
                if user_input.lower() in ("exit", "quit"):
                    print("Goodbye!")
                    break

                messages.append({"role": "user", "content": user_input})

                # Agentic loop — keep going until Claude stops calling tools
                while True:
                    response = claude.messages.create(
                        model="claude-opus-4-6",
                        max_tokens=4096,
                        system=SYSTEM_PROMPT,
                        tools=tools,
                        messages=messages,
                    )

                    # Append assistant response to history
                    messages.append({"role": "assistant", "content": response.content})

                    # Print any text blocks
                    for block in response.content:
                        if block.type == "text" and block.text:
                            print(f"\nAssistant: {block.text}\n")

                    # Done if no more tool calls
                    if response.stop_reason == "end_turn":
                        break

                    # Execute tool calls
                    tool_use_blocks = [b for b in response.content if b.type == "tool_use"]
                    if not tool_use_blocks:
                        break

                    tool_results = []
                    for tool_use in tool_use_blocks:
                        print(f"  [Tool] {tool_use.name}({tool_use.input})")
                        try:
                            result = await session.call_tool(tool_use.name, tool_use.input)
                            output = result.content[0].text if result.content else ""
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": tool_use.id,
                                "content": output,
                            })
                        except Exception as e:
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": tool_use.id,
                                "content": f"Error: {str(e)}",
                                "is_error": True,
                            })

                    messages.append({"role": "user", "content": tool_results})


if __name__ == "__main__":
    asyncio.run(main())

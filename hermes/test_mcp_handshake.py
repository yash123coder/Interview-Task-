import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    project_root = Path(__file__).resolve().parents[1]
    server_file = project_root / "hermes" / "server.py"

    params = StdioServerParameters(
        command=sys.executable,
        args=[str(server_file)],
        cwd=str(project_root),
    )

    print("Starting MCP server subprocess...")

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            print("Initializing MCP session...")
            init_result = await session.initialize()

            print("MCP handshake: SUCCESS")
            print("Server information:", init_result.server_info.name)
            print("Server version:", init_result.server_info.version)

            result = await session.list_tools()

            print("\nTools discovered through MCP protocol:")
            for tool in result.tools:
                print("-", tool.name, "|", tool.description)

            print("\nTotal tools discovered:", len(result.tools))

            expected = {"lookup_lead", "update_lead_status"}
            actual = {tool.name for tool in result.tools}

            if actual == expected:
                print("RESULT: PASS")
            else:
                print("RESULT: FAIL")
                print("Expected:", expected)
                print("Actual:", actual)


if __name__ == "__main__":
    asyncio.run(main())

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

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            print("TEST 1: Attempt restricted CONVERTED status")

            restricted = await session.call_tool(
                "update_lead_status",
                {"lead_id": 1, "sales_status": "CONVERTED"},
            )

            for item in restricted.content:
                if hasattr(item, "text"):
                    print(item.text)

            print("MCP error flag:", restricted.is_error)

            print("\nTEST 2: Set permitted CONTACTED status")

            permitted = await session.call_tool(
                "update_lead_status",
                {"lead_id": 1, "sales_status": "CONTACTED"},
            )

            for item in permitted.content:
                if hasattr(item, "text"):
                    print(item.text)

            print("MCP error flag:", permitted.is_error)


if __name__ == "__main__":
    asyncio.run(main())

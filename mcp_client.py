import asyncio
from contextlib import AsyncExitStack
from typing import Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPClient:
    """A client for interacting with a Model Context Protocol (MCP) server."""

    def __init__(self):
        """Initializes the MCPClient."""
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

    async def connect(self, server_script_path: str):
        """
        Connects to an MCP server using the specified server script.

        Args:
            server_script_path: The path to the server script to connect to.
        """
        if not server_script_path.endswith((".py", ".js")):
            raise ValueError("Server script must be a .py or .js file")

        command = "python" if server_script_path.endswith(".py") else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None,
        )

        read_stream, write_stream = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )

        await self.session.initialize()
        print("MCP client connected.")

    async def disconnect(self):
        """Disconnects from the MCP server and cleans up resources."""
        await self.exit_stack.aclose()
        print("MCP client disconnected.")

    async def list_tools(self):
        """Lists the available tools from the connected MCP server."""
        if not self.session:
            raise ConnectionError("Not connected to an MCP server.")
        response = await self.session.list_tools()
        return response.tools

    async def call_tool(self, tool_name: str, arguments: dict):
        """
        Calls a tool on the connected MCP server.

        Args:
            tool_name: The name of the tool to call.
            arguments: The arguments to pass to the tool.

        Returns:
            The result of the tool call.
        """
        if not self.session:
            raise ConnectionError("Not connected to an MCP server.")
        result = await self.session.call_tool(tool_name, arguments)
        return result.content 
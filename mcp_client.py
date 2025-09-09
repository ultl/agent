import asyncio

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStreamableHTTP

from constant import model

server = MCPServerStreamableHTTP('http://localhost:8000/mcp')
agent = Agent(model=model, toolsets=[server])


async def main():
  async with agent:
    result = await agent.run('What is 7 plus 5?')
  print(result.output)


asyncio.run(main())

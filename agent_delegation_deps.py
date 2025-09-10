import asyncio
from dataclasses import dataclass

import httpx
from byeprint import p
from pydantic_ai import Agent, RunContext

from constant import model


@dataclass
class ClientAndKey:
  http_client: httpx.AsyncClient
  api_key: str


joke_selection_agent = Agent(
  model=model,
  deps_type=ClientAndKey,
  system_prompt=(
    'Use the `joke_factory` tool to generate some jokes on the given subject, '
    'then choose the best. You must return just a single joke.'
  ),
)
joke_generation_agent = Agent(
  model=model,
  deps_type=ClientAndKey,
  output_type=list[str],
  system_prompt=(
    'Use the "get_jokes" tool to get some jokes on the given subject, then extract each joke into a list.'
  ),
)


@joke_selection_agent.tool
async def joke_factory(ctx: RunContext[ClientAndKey], count: int) -> list[str]:
  r = await joke_generation_agent.run(
    f'Please generate {count} jokes.',
    deps=ctx.deps,  # type: ignore
    usage=ctx.usage,
  )
  return r.output


@joke_generation_agent.tool
async def get_jokes(ctx: RunContext[ClientAndKey], count: int) -> str:
  response = await ctx.deps.http_client.get(
    'https://example.com',
    params={'count': count},
    headers={'Authorization': f'Bearer {ctx.deps.api_key}'},
  )
  p(response)
  response.raise_for_status()
  p(response.raise_for_status())
  return response.text


async def main():
  async with httpx.AsyncClient() as client:
    deps = ClientAndKey(client, 'foobar')
    p(deps)
    result = await joke_selection_agent.run('Tell me a joke.', deps=deps)
    p(result.output)
    p(result.usage())


asyncio.run(main())

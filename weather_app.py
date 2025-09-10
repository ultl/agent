from __future__ import annotations as _annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from byeprint import p
from httpx import AsyncClient
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

from constant import model


@dataclass
class Deps:
  client: AsyncClient


weather_agent = Agent(
  model=model,
  instructions='Be concise, reply with one sentence.',
  deps_type=Deps,
  retries=2,
)


class LatLng(BaseModel):
  lat: float
  lng: float


@weather_agent.tool
async def get_lat_lng(ctx: RunContext[Deps], location_description: str) -> LatLng:
  r = await ctx.deps.client.get(
    url='https://demo-endpoints.pydantic.workers.dev/latlng',
    params={'location': location_description},
  )
  r.raise_for_status()
  p(r.raise_for_status())
  p(r.content)
  p(LatLng.model_validate_json(r.content))
  return LatLng.model_validate_json(r.content)


@weather_agent.tool
async def get_weather(ctx: RunContext[Deps], lat: float, lng: float) -> dict[str, Any]:
  temp_response, descr_response = await asyncio.gather(
    ctx.deps.client.get(
      url='https://demo-endpoints.pydantic.workers.dev/number',
      params={'min': 10, 'max': 30},
    ),
    ctx.deps.client.get(
      url='https://demo-endpoints.pydantic.workers.dev/weather',
      params={'lat': lat, 'lng': lng},
    ),
  )
  temp_response.raise_for_status()
  descr_response.raise_for_status()
  p(temp_response.raise_for_status())
  p(descr_response.raise_for_status())
  p({
    'temperature': f'{temp_response.text} °C',
    'description': descr_response.text,
  })
  return {
    'temperature': f'{temp_response.text} °C',
    'description': descr_response.text,
  }


async def main() -> None:
  async with AsyncClient() as client:
    deps = Deps(client=client)
    result = await weather_agent.run('What is the weather like in Vietnam and in Wiltshire?', deps=deps)  # type: ignore
    p('Response:', result.output)


if __name__ == '__main__':
  asyncio.run(main())

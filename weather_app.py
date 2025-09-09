from __future__ import annotations as _annotations

import asyncio
from dataclasses import dataclass, field
from datetime import UTC, date
from itertools import starmap
from typing import Any

import pytest
from dirty_equals import IsNow, IsStr
from pydantic_ai import Agent, RequestUsage, RunContext, capture_run_messages, models
from pydantic_ai.messages import (
  ModelRequest,
  ModelResponse,
  SystemPromptPart,
  TextPart,
  ToolCallPart,
  ToolReturnPart,
  UserPromptPart,
)
from pydantic_ai.models.test import TestModel

from constant import model


class WeatherService:
  def get_historic_weather(self, location: str, forecast_date: date) -> str:
    return 'Sunny with a chance of rain'

  def get_forecast(self, location: str, forecast_date: date) -> str:
    return 'Rainy with a chance of sun'

  async def __aenter__(self) -> WeatherService:
    return self

  async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
    pass


class FakeTable:
  def get(self, name: str) -> int | None:
    if name == 'John Doe':
      return 123


@dataclass
class DatabaseConn:
  users: FakeTable = field(default_factory=FakeTable)
  _forecasts: dict[int, str] = field(default_factory=dict)

  async def execute(self, query: str) -> list[dict[str, Any]]:
    return [{'id': 123, 'name': 'John Doe'}]

  async def store_forecast(self, user_id: int, forecast: str) -> None:
    self._forecasts[user_id] = forecast

  async def get_forecast(self, user_id: int) -> str | None:
    return self._forecasts.get(user_id)


class QueryError(RuntimeError):
  pass


weather_agent = Agent(
  model=model,
  deps_type=WeatherService,
  system_prompt='Providing a weather forecast at the locations the user provides.',
)


@weather_agent.tool
def weather_forecast(ctx: RunContext[WeatherService], location: str, forecast_date: date) -> str:
  if forecast_date < date.today():
    return ctx.deps.get_historic_weather(location, forecast_date)
  return ctx.deps.get_forecast(location, forecast_date)


async def run_weather_forecast(user_prompts: list[tuple[str, int]], conn: DatabaseConn):
  """Run weather forecast for a list of user prompts and save."""
  async with WeatherService() as weather_service:

    async def run_forecast(prompt: str, user_id: int):
      result = await weather_agent.run(prompt, deps=weather_service)
      await conn.store_forecast(user_id, result.output)

    # run all prompts in parallel
    await asyncio.gather(*starmap(run_forecast, user_prompts))


pytestmark = pytest.mark.anyio
models.ALLOW_MODEL_REQUESTS = False


async def test_forecast():
  conn = DatabaseConn()
  user_id = 1
  with capture_run_messages() as messages, weather_agent.override(model=TestModel()):
    prompt = 'What will the weather be like in London on 2024-11-28?'
    await run_weather_forecast([(prompt, user_id)], conn)

  forecast = await conn.get_forecast(user_id)
  assert forecast == '{"weather_forecast":"Sunny with a chance of rain"}'

  assert messages == [
    ModelRequest(
      parts=[
        SystemPromptPart(
          content='Providing a weather forecast at the locations the user provides.',
          timestamp=IsNow(tz=UTC),
        ),
        UserPromptPart(
          content='What will the weather be like in London on 2024-11-28?',
          timestamp=IsNow(tz=UTC),
        ),
      ]
    ),
    ModelResponse(
      parts=[
        ToolCallPart(
          tool_name='weather_forecast',
          args={
            'location': 'a',
            'forecast_date': '2024-01-01',
          },
          tool_call_id=IsStr(),
        )
      ],
      usage=RequestUsage(
        input_tokens=71,
        output_tokens=7,
      ),
      model_name='test',
      timestamp=IsNow(tz=UTC),
    ),
    ModelRequest(
      parts=[
        ToolReturnPart(
          tool_name='weather_forecast',
          content='Sunny with a chance of rain',
          tool_call_id=IsStr(),
          timestamp=IsNow(tz=UTC),
        ),
      ],
    ),
    ModelResponse(
      parts=[
        TextPart(
          content='{"weather_forecast":"Sunny with a chance of rain"}',
        )
      ],
      usage=RequestUsage(
        input_tokens=77,
        output_tokens=16,
      ),
      model_name='test',
      timestamp=IsNow(tz=UTC),
    ),
  ]


asyncio.run(test_forecast())

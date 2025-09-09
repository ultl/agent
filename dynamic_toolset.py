from dataclasses import dataclass
from typing import Literal

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.test import TestModel

from function_toolset import datetime_toolset, weather_toolset


@dataclass
class ToggleableDeps:
  active: Literal['weather', 'datetime']

  def toggle(self):
    if self.active == 'weather':
      self.active = 'datetime'
    else:
      self.active = 'weather'


test_model = TestModel()
agent = Agent(test_model, deps_type=ToggleableDeps)


@agent.toolset
def toggleable_toolset(ctx: RunContext[ToggleableDeps]):
  if ctx.deps.active == 'weather':
    return weather_toolset
  return datetime_toolset


@agent.tool
def toggle(ctx: RunContext[ToggleableDeps]):
  ctx.deps.toggle()


deps = ToggleableDeps('weather')

result = agent.run_sync('Toggle the toolset', deps=deps)
print([t.name for t in test_model.last_model_request_parameters.function_tools])
# > ['toggle', 'now']

result = agent.run_sync('Toggle the toolset', deps=deps)
print([t.name for t in test_model.last_model_request_parameters.function_tools])
# > ['toggle', 'temperature_celsius', 'temperature_fahrenheit', 'conditions']

from byeprint import p
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel
from pydantic_ai.toolsets import CombinedToolset

from function_toolset import datetime_toolset, weather_toolset

combined_toolset = CombinedToolset([weather_toolset, datetime_toolset])
p(weather_toolset.prefixed('weather'))
combined_toolset = CombinedToolset([weather_toolset.prefixed('weather'), datetime_toolset.prefixed('datetime')])

test_model = TestModel()
agent = Agent(test_model, toolsets=[combined_toolset])
result = agent.run_sync('What tools are available?')
p([t.name for t in test_model.last_model_request_parameters.function_tools])

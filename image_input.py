from pydantic_ai import Agent, ImageUrl

from constant import model

agent = Agent(model=model)
result = agent.run_sync([
  'What company is this logo from?',
  ImageUrl(url='https://iili.io/3Hs4FMg.png'),
])
print(result.output)

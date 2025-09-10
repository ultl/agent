import asyncio
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext, RunUsage, UsageLimits
from pydantic_ai.messages import ModelMessage
from rich.prompt import Prompt

from constant import model


class FlightDetails(BaseModel):
  flight_number: str


class Failed(BaseModel):
  """Unable to find a satisfactory choice."""


flight_search_agent = Agent[None, FlightDetails | Failed](
  model=model,
  output_type=FlightDetails | Failed,  # type: ignore
  system_prompt=('Use the "flight_search" tool to find a flight from the given origin to the given destination.'),
)


@flight_search_agent.tool
async def flight_search(ctx: RunContext[None], origin: str, destination: str) -> FlightDetails | None:
  # in reality, this would call a flight search API or
  # use a browser to scrape a flight search website
  return FlightDetails(flight_number='AK456')


usage_limits = UsageLimits(request_limit=15)


async def find_flight(usage: RunUsage) -> FlightDetails | None:
  message_history: list[ModelMessage] | None = None
  for _ in range(3):
    prompt = Prompt.ask(
      'Where would you like to fly from and to?',
    )
    result = await flight_search_agent.run(
      prompt,
      message_history=message_history,
      usage=usage,
      usage_limits=usage_limits,
    )
    if isinstance(result.output, FlightDetails):
      return result.output
    message_history = result.all_messages(output_tool_return_content='Please try again.')
  return None


class SeatPreference(BaseModel):
  row: int = Field(ge=1, le=30)
  seat: Literal['A', 'B', 'C', 'D', 'E', 'F']


# This agent is responsible for extracting the user's seat selection
seat_preference_agent = Agent[None, SeatPreference | Failed](
  model=model,
  output_type=SeatPreference | Failed,  # type: ignore
  system_prompt=(
    "Extract the user's seat preference. "
    'Seats A and F are window seats. '
    'Row 1 is the front row and has extra leg room. '
    'Rows 14, and 20 also have extra leg room. '
  ),
)


async def find_seat(usage: RunUsage) -> SeatPreference:
  message_history: list[ModelMessage] | None = None
  while True:
    answer = Prompt.ask('What seat would you like?')

    result = await seat_preference_agent.run(
      answer,
      message_history=message_history,
      usage=usage,
      usage_limits=usage_limits,
    )
    if isinstance(result.output, SeatPreference):
      return result.output
    print('Could not understand seat preference. Please try again.')
    message_history = result.all_messages()


async def main():
  usage: RunUsage = RunUsage()

  opt_flight_details = await find_flight(usage)
  if opt_flight_details is not None:
    print(f'Flight found: {opt_flight_details.flight_number}')
    # > Flight found: AK456
    seat_preference = await find_seat(usage)
    print(f'Seat preference: {seat_preference}')
    # > Seat preference: row=1 seat='A'


asyncio.run(main())

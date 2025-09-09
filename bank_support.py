import asyncio
from dataclasses import dataclass

from byeprint import p
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

from constant import model


class DatabaseConn:
  """This is a fake database for example purposes.

  In reality, you'd be connecting to an external database
  (e.g. PostgreSQL) to get information about customers.
  """

  @classmethod
  async def customer_name(cls, *, id: int) -> str | None:
    if id == 123:
      return 'John'

  @classmethod
  async def customer_balance(cls, *, id: int, include_pending: bool) -> float:
    if id == 123:
      if include_pending:
        return 123.45
      return 100.00
    raise ValueError('Customer not found')


@dataclass
class SupportDependencies:
  customer_id: int
  db: DatabaseConn


class SupportOutput(BaseModel):
  support_advice: str
  """Advice returned to the customer"""
  block_card: bool
  """Whether to block their card or not"""
  risk: int
  """Risk level of query"""


support_agent = Agent(
  model=model,
  deps_type=SupportDependencies,
  output_type=SupportOutput,
  instructions=(
    'You are a support agent in our bank, give the '
    'customer support and judge the risk level of their query. '
    "Reply using the customer's name."
  ),
)


@support_agent.instructions
async def add_customer_name(ctx: RunContext[SupportDependencies]) -> str:
  customer_name = await ctx.deps.db.customer_name(id=ctx.deps.customer_id)
  return f"The customer's name is {customer_name!r}"


@support_agent.tool
async def customer_balance(ctx: RunContext[SupportDependencies], include_pending: bool) -> str:
  """Returns the customer's current account balance."""
  balance = await ctx.deps.db.customer_balance(
    id=ctx.deps.customer_id,
    include_pending=include_pending,
  )
  return f'${balance:.2f}'


deps = SupportDependencies(customer_id=123, db=DatabaseConn())


async def main():
  nodes = []
  async with support_agent.iter('What is my balance?', deps=deps) as agent_run:
    async for node in agent_run:
      nodes.append(node)
  p(nodes)


asyncio.run(main())

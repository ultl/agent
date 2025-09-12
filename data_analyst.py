from dataclasses import dataclass, field

import datasets
import duckdb
import pandas as pd
from byeprint import p
from pydantic_ai import Agent, ModelRetry, RunContext

from constant import model


@dataclass
class AnalystAgentDeps:
  output: dict[str, pd.DataFrame] = field(default_factory=dict)

  def store(self, value: pd.DataFrame) -> str:
    """Store the output in deps and return the reference such as Out[1] to be used by the LLM."""
    ref = f'Out[{len(self.output) + 1}]'
    p(ref)
    self.output[ref] = value
    return ref

  def get(self, ref: str) -> pd.DataFrame:
    if ref not in self.output:
      raise ModelRetry(f'Error: {ref} is not a valid variable reference. Check the previous messages and try again.')
    return self.output[ref]


analyst_agent = Agent(
  model=model,
  deps_type=AnalystAgentDeps,
  instructions='You are a data analyst and your job is to analyze the data according to the user request.',
)


@analyst_agent.tool
def load_dataset(
  ctx: RunContext[AnalystAgentDeps],
  path: str,
  split: str = 'train',
) -> str:
  """Load the `split` of dataset `dataset_name` from huggingface.

  Args:
      ctx: Pydantic AI agent RunContext
      path: name of the dataset in the form of `<user_name>/<dataset_name>`
      split: load the split of the dataset (default: "train")
  """
  builder = datasets.load_dataset_builder(path)  # pyright: ignore[reportUnknownMemberType]
  p(builder)
  splits: dict[str, datasets.SplitInfo] = builder.info.splits or {}  # pyright: ignore[reportUnknownMemberType]
  p(splits)
  if split not in splits:
    raise ModelRetry(f'{split} is not valid for dataset {path}. Valid splits are {",".join(splits.keys())}')

  builder.download_and_prepare()  # pyright: ignore[reportUnknownMemberType]
  dataset = builder.as_dataset(split=split)
  p(dataset)
  assert isinstance(dataset, datasets.Dataset)
  dataframe = dataset.to_pandas()
  assert isinstance(dataframe, pd.DataFrame)
  ref = ctx.deps.store(dataframe)
  p(ref)
  output = [
    f'Loaded the dataset as `{ref}`.',
    f'Description: {dataset.info.description}' if dataset.info.description else None,
    f'Features: {dataset.info.features!r}' if dataset.info.features else None,
  ]
  return '\n'.join(filter(None, output))


@analyst_agent.tool
def run_duckdb(ctx: RunContext[AnalystAgentDeps], dataset: str, sql: str) -> str:
  """Run DuckDB SQL query on the DataFrame.

  Note that the virtual table name used in DuckDB SQL must be `dataset`.

  Args:
      ctx: Pydantic AI agent RunContext
      dataset: reference string to the DataFrame
      sql: the query to be executed using DuckDB
  """
  data = ctx.deps.get(dataset)
  result = duckdb.query_df(df=data, virtual_table_name='dataset', sql_query=sql)
  ref = ctx.deps.store(result.df())  # pyright: ignore[reportUnknownMemberType]
  return f'Executed SQL, result is `{ref}`'


@analyst_agent.tool
def display(ctx: RunContext[AnalystAgentDeps], name: str) -> str:
  """Display at most 5 rows of the dataframe."""
  dataset = ctx.deps.get(name)
  return dataset.head().to_string()  # pyright: ignore[reportUnknownMemberType]


if __name__ == '__main__':
  deps = AnalystAgentDeps()
  result = analyst_agent.run_sync(
    user_prompt='Load the dataset `cornell-movie-review-data/rotten_tomatoes`',
    deps=deps,
  )
  p(result.output)

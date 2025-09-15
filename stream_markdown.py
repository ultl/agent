import asyncio
import os

from dotenv import load_dotenv
from pydantic_ai import Agent
from rich.console import Console, ConsoleOptions, RenderResult
from rich.live import Live
from rich.markdown import CodeBlock, Markdown
from rich.syntax import Syntax
from rich.text import Text

load_dotenv()
agent = Agent()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
models = [
  ('openai/gpt-oss-20b', OPENAI_API_KEY),
]


async def main():
  prettier_code_blocks()
  console = Console()
  prompt = 'Show me a short example of using Pydantic.'
  console.log(f'Asking: {prompt}...', style='cyan')
  for model, env_var in models:
    if env_var in os.environ:
      console.log(f'Using model: {model}')
      with Live('', console=console, vertical_overflow='visible') as live:
        async with agent.run_stream(prompt, model=model) as result:
          async for message in result.stream_output():
            live.update(Markdown(message))
      console.log(result.usage())
    else:
      console.log(f'{model} requires {env_var} to be set.')


def prettier_code_blocks():
  """Make rich code blocks prettier and easier to copy.

  From https://github.com/samuelcolvin/aicli/blob/v0.8.0/samuelcolvin_aicli.py#L22
  """

  class SimpleCodeBlock(CodeBlock):
    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
      code = str(self.text).rstrip()
      yield Text(self.lexer_name, style='dim')
      yield Syntax(
        code,
        self.lexer_name,
        theme=self.theme,
        background_color='default',
        word_wrap=True,
      )
      yield Text(f'/{self.lexer_name}', style='dim')

  Markdown.elements['fence'] = SimpleCodeBlock


if __name__ == '__main__':
  asyncio.run(main())

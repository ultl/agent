import logfire
from dotenv import load_dotenv
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

load_dotenv()


logfire.configure(
  service_name='my-service-1',
  send_to_logfire=False,
)
logfire.instrument_pydantic_ai()

MODEL_NAME = 'openai/gpt-oss-20b'
ANOTHER_MODEL_NAME = 'openreasoning-nemotron-32b'
PROVIDER = OpenAIProvider(base_url='http://localhost:1234/v1')
model = OpenAIChatModel(model_name=MODEL_NAME, provider=PROVIDER)
another_model = OpenAIChatModel(model_name=ANOTHER_MODEL_NAME, provider=PROVIDER)

import os

import logfire
from dotenv import load_dotenv
from openai import OpenAI
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

load_dotenv()


OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
logfire.configure(
  service_name='my-service-1',
  send_to_logfire=False,
)
logfire.instrument_pydantic_ai()

MODEL_NAME = 'openai/gpt-oss-20b'
ANOTHER_MODEL_NAME = 'openreasoning-nemotron-32b'

CLIENT = OpenAI(base_url=OPENAI_BASE_URL, api_key=OPENAI_API_KEY)
PROVIDER = OpenAIProvider(base_url=OPENAI_BASE_URL)
model = OpenAIChatModel(model_name=MODEL_NAME, provider=PROVIDER)
another_model = OpenAIChatModel(model_name=ANOTHER_MODEL_NAME, provider=PROVIDER)

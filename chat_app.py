from __future__ import annotations as _annotations

import json
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, Literal

import fastapi
from fastapi import Depends
from fastapi.responses import FileResponse, Response, StreamingResponse
from pydantic_ai import Agent, UnexpectedModelBehavior
from pydantic_ai.messages import (
  ModelMessage,
  ModelRequest,
  ModelResponse,
  TextPart,
  UserPromptPart,
)
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing_extensions import TypedDict

from constant import model

agent = Agent(model=model)
THIS_DIR = Path(__file__).parent


class ChatMessageDB(SQLModel, table=True):
  id: int | None = Field(default=None, primary_key=True)
  message_json: str


sqlite_file_name = 'database.db'
sqlite_url = f'sqlite:///{sqlite_file_name}'
connect_args = {'check_same_thread': False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
  SQLModel.metadata.create_all(engine)


def get_session():
  with Session(engine) as session:
    yield session


SessionDep = Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(_app: fastapi.FastAPI):
  create_db_and_tables()
  yield


app = fastapi.FastAPI(lifespan=lifespan)


@app.get('/')
async def index() -> FileResponse:
  return FileResponse('chat_app.html', media_type='text/html')


@app.get('/chat_app.ts')
async def main_ts() -> FileResponse:
  return FileResponse('chat_app.ts', media_type='text/plain')


class ChatMessage(TypedDict):
  """Format of messages sent to the browser."""

  role: Literal['user', 'model']
  timestamp: str
  content: str


def to_chat_message(m: ModelMessage) -> ChatMessage:
  first_part = m.parts[0]
  if isinstance(m, ModelRequest):
    if isinstance(first_part, UserPromptPart):
      assert isinstance(first_part.content, str)
      return {
        'role': 'user',
        'timestamp': first_part.timestamp.isoformat(),
        'content': first_part.content,
      }
  elif isinstance(m, ModelResponse):
    if isinstance(first_part, TextPart):
      return {
        'role': 'model',
        'timestamp': m.timestamp.isoformat(),
        'content': first_part.content,
      }
  raise UnexpectedModelBehavior(f'Unexpected message type for chat app: {m}')


def get_messages_from_db(session: Session) -> list[ModelMessage]:
  """Get all messages from database and convert back to ModelMessage objects"""
  statement = select(ChatMessageDB)
  results = session.exec(statement)
  messages = []

  for db_message in results:
    # Parse the JSON back to ModelMessage
    message_data = json.loads(db_message.message_json)

  return messages


def add_messages_to_db(session: Session, messages_json: str):
  messages_data = json.loads(messages_json)

  for message_data in messages_data:
    db_message = ChatMessageDB(message_json=json.dumps(message_data))
    session.add(db_message)

  session.commit()


@app.get('/chat/')
async def get_chat(session: SessionDep) -> Response:
  messages = get_messages_from_db(session)
  return Response(
    b'\n'.join(json.dumps(to_chat_message(m)).encode('utf-8') for m in messages),
    media_type='text/plain',
  )


@app.post('/chat/')
async def post_chat(prompt: Annotated[str, fastapi.Form()], session: SessionDep) -> StreamingResponse:
  async def stream_messages():
    """Streams new line delimited JSON `Message`s to the client."""
    # stream the user prompt so that can be displayed straight away
    yield (
      json.dumps({
        'role': 'user',
        'timestamp': datetime.now(tz=UTC).isoformat(),
        'content': prompt,
      }).encode('utf-8')
      + b'\n'
    )

    # get the chat history so far to pass as context to the agent
    messages = get_messages_from_db(session)

    # run the agent with the user prompt and the chat history
    async with agent.run_stream(prompt, message_history=messages) as result:
      async for text in result.stream_output(debounce_by=0.01):
        # text here is a `str` and the frontend wants
        # JSON encoded ModelResponse, so we create one
        m = ModelResponse(parts=[TextPart(text)], timestamp=result.timestamp())
        yield json.dumps(to_chat_message(m)).encode('utf-8') + b'\n'

    # add new messages to the database
    add_messages_to_db(session, result.new_messages_json())

  return StreamingResponse(stream_messages(), media_type='text/plain')

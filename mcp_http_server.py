from mcp.server.fastmcp import FastMCP

app = FastMCP()


@app.tool()
def add(a: int, b: int) -> int:
  return a + b


app.run(transport='streamable-http')

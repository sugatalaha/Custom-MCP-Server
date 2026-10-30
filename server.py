from mcp.server import MCPServer
import logging
from tools.file_tools import *
import utils.path_utils as utils
from pathlib import Path
import json

CONFIG_PATH="/home/sugatalinux/projects/codebase-mcp/MCP-Server.json"

with open(CONFIG_PATH) as f:
    config=json.load(f)

CODEBASE_PATH=Path(config["root_path"])
max_lines=config["max_lines"]
max_matches_allowed=config["max_matches_allowed"]
log_path=config["log_path"]

mcp=MCPServer("Legacy Codebase MCP Server")

logging.basicConfig(
    filename=log_path,
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    force=True
)

logger = logging.getLogger(__name__)

@mcp.tool()
def hello(name:str)->str:
    return f"Hello, {name}"

mcp.tool()(create_list_files(CODEBASE_PATH)) 

mcp.tool()(create_read_file(CODEBASE_PATH, max_lines))

mcp.tool()(create_search_code(CODEBASE_PATH, max_matches_allowed))

if __name__=="__main__":
    mcp.run()
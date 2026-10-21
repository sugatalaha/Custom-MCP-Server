from mcp.server import MCPServer
import logging
import utils
from pathlib import Path
import json

CODEBASE_PATH=Path("/home/sugatalinux/projects")

mcp=MCPServer("Legacy Codebase MCP Server")
max_lines=200

logging.basicConfig(
    filename="/home/sugatalinux/projects/codebase-mcp/codebase-mcp.log",
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    force=True
)

logger = logging.getLogger(__name__)

logger.info("===== MCP SERVER STARTED =====")
logger.debug("Debug logging is working")

@mcp.tool()
def hello(name:str)->str:
    return f"Hello, {name}"

@mcp.tool()
def list_files(path:str=".")->str:
    logger.info("list_files called with path: %s", path)
    files=[]
    flag, reason_or_path=utils.check_is_valid_path(path, CODEBASE_PATH)
    if not flag:
        logger.warning("Path is not valid : reason %s", reason_or_path)
        return reason_or_path
    logger.info("Resolved path is %s", reason_or_path)
    utils.recursive_file_list(files, reason_or_path)
    logger.info("Found %d files ", len(files))
    return "\n".join(sorted(str(file) for file in files))

@mcp.tool()
def read_file(path:str, start_line:int, end_line:int|None)->str:
    pathObject=Path(CODEBASE_PATH/Path(path)).resolve()
    flag, reason=utils.validate_start_and_end_line(pathObject, start_line, end_line)
    if not flag:
        return reason
    truncated=False
    end_line_new=end_line
    toReturnDict={}
    if end_line is None or end_line-start_line+1>=max_lines:
        end_line_new=start_line+max_lines-1
    count=1
    lines=[]
    with open(str(pathObject)) as f:
        for line in f:
            if count>=start_line:
                if count<=end_line_new:
                    lines.append(f"{count}: {line}")
                else:
                    break
            count+=1
    content="\n".join(lines)
    toReturnDict["truncated"]=truncated
    toReturnDict["start_line"]=start_line
    toReturnDict["end_line"]=end_line_new
    toReturnDict["max_lines"]=max_lines
    toReturnDict["content"]=content
    return json.dumps(toReturnDict)

    


if __name__=="__main__":
    mcp.run()
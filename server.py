from mcp.server import MCPServer
import logging
import utils
from pathlib import Path
import json

CODEBASE_PATH=Path("/home/sugatalinux/projects/codebase-mcp/source-code")

mcp=MCPServer("Legacy Codebase MCP Server")
max_lines=200
max_matches_allowed=2000

logging.basicConfig(
    filename="/home/sugatalinux/projects/codebase-mcp/codebase-mcp.log",
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    force=True
)

logger = logging.getLogger(__name__)

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
def read_file(path:str, start_line:int, end_line:int|None=None)->str:
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
    toReturnDict["truncated"]=truncated
    toReturnDict["start_line"]=start_line
    toReturnDict["end_line"]=end_line_new
    toReturnDict["max_lines"]=max_lines
    toReturnDict["content"]=lines
    return json.dumps(toReturnDict)

    
@mcp.tool()
def search_code(pattern:str, path:str='.', is_regex:bool=False):
    path_to_search=Path(CODEBASE_PATH/Path(path)).resolve()
    if not path_to_search.exists():
        logging.warning("Path %s does not exist", str(path_to_search))
        return f"Path {str(path_to_search)} does not exist"
    if not is_regex:
        list_pattern_matches=[]
        truncated=utils.recursive_search_pattern_no_regex(path_to_search, pattern, list_pattern_matches, max_matches_allowed)
        matches=len(list_pattern_matches)
        toReturnObject={}
        toReturnObject["matches"]=matches
        toReturnObject["truncated"]=truncated
        toReturnObject["content"]=list_pattern_matches
        toReturnObject["max_matches_allowed"]=max_matches_allowed
        logging.info("Number of instances matched with literal %s is %d", str(path_to_search), list_pattern_matches)
        return json.dumps(toReturnObject)

if __name__=="__main__":
    mcp.run()
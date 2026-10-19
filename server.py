from mcp.server import MCPServer
import os
import utils

codebase_path="/home/sugatalinux/projects"

mcp=MCPServer("Legacy Codebase MCP Server")

@mcp.tool()
def hello(name:str)->str:
    return f"Hello, {name}"

@mcp.tool()
def list_files(path:str=".")->str:
    files=[]
    path_to_search=""
    if path==".":
        path_to_search=codebase_path
    elif path[0]=="/":
        return "You can give only path relative to the codebase"
    else:
        if path not in os.listdir(codebase_path):
            return f"Path {path} you are searching is not in codebase"
        else:
            path_to_search=os.path.join(codebase_path, path)
    utils.dfs(files, path_to_search)
    return "\n".join(sorted(files))

@mcp.tool()
def read_file(path:str="")->str:
    pass

if __name__=="__main__":
    mcp.run()
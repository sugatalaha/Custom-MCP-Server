import logging
import utils.path_utils as utils
from pathlib import Path
import json

logger=logging.getLogger(__name__)

def create_list_files(codebase_path:str):
    def list_files(path:str=".")->str:
        logger.info("list_files called with path: %s", path)
        files=[]
        flag, reason_or_path=utils.check_is_valid_path(path, codebase_path)
        if not flag:
            logger.warning("Path is not valid : reason %s", reason_or_path)
            return reason_or_path
        logger.info("Resolved path is %s", reason_or_path)
        utils.recursive_file_list(files, reason_or_path)
        logger.info("Found %d files ", len(files))
        return "\n".join(sorted(str(file) for file in files))
    return list_files

def create_read_file(codebase_path:str, max_lines:int):
    def read_file(path:str, start_line:int, end_line:int|None=None)->str:
        flag, reason_or_path=utils.check_is_valid_path(path, codebase_path, file_required=True)
        if not flag:
            logger.warning("Path is not valid : reason %s", reason_or_path)
            return reason_or_path
        if Path(reason_or_path).is_dir():
            logger.warning("Path %s represents a directory", reason_or_path)
            return f"Path {reason_or_path} represents a directory. Give a file path"
        pathObject=Path(codebase_path/Path(path)).resolve()
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
                        truncated=True
                        break
                count+=1
        toReturnDict["truncated"]=truncated
        toReturnDict["start_line"]=start_line
        toReturnDict["end_line"]=end_line_new
        toReturnDict["max_lines"]=max_lines
        toReturnDict["content"]=lines
        return json.dumps(toReturnDict)

    return read_file

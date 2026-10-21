import re
from pathlib import Path
import logging

logger=logging.getLogger(__name__)

INCLUDE = re.compile(r"\.(c|cc|cpp|h|hpp|java|py)$")
EXCLUDE_DIRECTORY=re.compile(r"\.[a-z]*")

def recursive_file_list(file_list, parent_dir:Path):
    if parent_dir.is_file():
        if INCLUDE.search(str(parent_dir)):
            file_list.append(parent_dir)    
        return
    for path in parent_dir.iterdir():
        if path.is_dir() and not EXCLUDE_DIRECTORY.search(str(path)):
            recursive_file_list(file_list, path.resolve())
        elif(INCLUDE.search(str(path))):
            file_list.append(path.resolve())

def check_is_valid_path(file_path:str, root_dir:Path):
    logger.debug("Validating path=%s against root=%s", file_path, root_dir)
    if Path(file_path).is_absolute():
        logger.warning("Absolute path rejected: %s", file_path)
        return False, f"Path {file_path} is absolute path. Provide path relative to codebase {root_dir}"
    requested_path=(root_dir/file_path).resolve()
    logger.debug("Resolved requested Path: %s", requested_path)
    if not requested_path.exists():
        logger.warning("Path does not exist %s", requested_path)
        return False, f"Path {requested_path.resolve()} does not exist"
    else:
        return True, requested_path

def validate_start_and_end_line(file_path_object:Path, start_line:int, end_line:int):
    logger.debug("Validating Start %d and end lines %d", start_line, end_line)
    if start_line<1:
        logger.warning("Start line %d is less than 1", start_line)
        return False, f"Start line {start_line} is less than 1"
    elif end_line is not None:
        if end_line <start_line:
            logger.warning("End Line %d is less than Start Line %d", end_line, start_line)
            return False, f"End line {end_line} is less than Start line {start_line}"
        size=0
        with open(str(file_path_object)) as f:
            size=len(f.readlines())
            if end_line-start_line+1>size:
                logger.warning("Number of lines requested %d is greater than the number of lines in file %s which is %d", end_line-start_line+1, str(file_path_object), size)
                return False, f"Number of lines requested {end_line-start_line+1} is greater than the number of lines in file {str(file_path_object)} which is {size}"
            else:
                return True, ""
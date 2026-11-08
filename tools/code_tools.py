import tree_sitter_c
import tree_sitter_cpp
import tree_sitter
from pathlib import Path
import logging
import json
from utils.parser import get_file_outline_helper
from utils.path_utils import check_is_valid_path
import utils.path_utils as utils

from tree_sitter import Language

C_LANGUAGE=Language(tree_sitter_c.language())
CPP_LANGUAGE=Language(tree_sitter_cpp.language())

oldTreeCPP=None
oldTreeC=None

logger=logging.getLogger(__name__)

def create_get_file_outline(codebase_path:str):
    def get_file_outline(path:str, include_functions:bool=True, include_types:bool=True, include_macros:bool=True, include_globals:bool=False):
        global oldTree
        flag, path_or_error=check_is_valid_path(path, codebase_path, file_required=True)
        if not flag:
            return path_or_error
        else:
            source_code_path=path_or_error
        toReturnObject={}
        try:
            with open(str(source_code_path)) as f:
                if(source_code_path.suffix in [".c", ".h"]):
                    parser=tree_sitter.Parser(C_LANGUAGE)
                    source_code_bytes=f.read()
                    global oldTreeC
                    if oldTreeC is None:
                        oldTreeC=parser.parse(source_code_bytes.encode())
                    else:
                        oldTreeC=parser.parse(source_code_bytes.encode(), oldTreeC)
                    toReturnObject["content"]=get_file_outline_helper(oldTreeC, C_LANGUAGE)
                    return json.dumps(toReturnObject)
                elif(source_code_path.suffix in [".cpp", ".hpp"]):
                    parser=tree_sitter.Parser(CPP_LANGUAGE)
                    source_code_bytes=f.read()
                    global oldTreeCPP
                    if oldTreeCPP is None:
                        oldTreeCPP=parser.parse(source_code_bytes.encode())
                    else:
                        oldTreeCPP=parser.parse(source_code_bytes.encode(), oldTreeCPP)
                    toReturnObject["content"]=get_file_outline_helper(oldTreeCPP, CPP_LANGUAGE,include_functions, include_types, include_macros, include_globals)
                    return json.dumps(toReturnObject)
                else:
                    logger.warning("Obtained suffix is %s", source_code_path.suffix)
                    return "Provide only C or C++ source files."
        except Exception as e:
            logger.warning("An exception occured in function get_file_outline: %s", str(e))
            return f"{e}"
    return get_file_outline

def create_search_code(codebase_path:str, max_matches_allowed:int):
    def search_code(pattern:str, path:str='.', is_regex:bool=False, offset:int=0):
        path_to_search=Path(codebase_path/Path(path)).resolve()
        flag, reason_or_path=utils.check_is_valid_path(path, codebase_path)
        if not flag:
            logger.warning("Path is not valid : reason %s", reason_or_path)
            return reason_or_path
        if not path_to_search.exists():
            logging.warning("Path %s does not exist", str(path_to_search))
            return f"Path {str(path_to_search)} does not exist"
        list_pattern_matches=[]
        toReturnObject={}
        if not is_regex:
            next_offset, has_more=utils.recursive_search_pattern_no_regex(path_to_search, pattern, list_pattern_matches, max_matches_allowed, offset)
            matches=len(list_pattern_matches)
        else:
            try:
                next_offset, has_more=utils.recurisve_search_pattern_regex(path_to_search, pattern, list_pattern_matches, max_matches_allowed, offset)
                matches=len(list_pattern_matches)
            except Exception as e:
                toReturnError={}
                toReturnError["error"]="Regex searching error"
                toReturnError["message"]=str(e)
                return json.dumps(toReturnError)
        toReturnObject["matches"]=matches
        toReturnObject["has_more"]=has_more
        toReturnObject["content"]=list_pattern_matches
        toReturnObject["max_matches_allowed"]=max_matches_allowed
        toReturnObject["next_offset"]=next_offset
        logging.info("Number of instances matched with literal %s is %d", str(path_to_search), len(list_pattern_matches))
        return json.dumps(toReturnObject)

    return search_code
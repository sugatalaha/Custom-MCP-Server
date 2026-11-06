import tree_sitter_c
import tree_sitter_cpp
import tree_sitter
from pathlib import Path
import logging
import json
from utils.parser import get_file_outline_helper

from tree_sitter import Language

C_LANGUAGE=Language(tree_sitter_c.language())
CPP_LANGUAGE=Language(tree_sitter_cpp.language())

oldTreeCPP=None
oldTreeC=None

logger=logging.getLogger(__name__)

def create_get_file_outline(codebase_path:str):
    def get_file_outline(path:str, include_functions:bool=True, include_types:bool=True, include_macros:bool=True, include_globals:bool=False):
        global oldTree
        source_code_path=Path.resolve(codebase_path/path)
        toReturnObject={}
        try:
            with open(str(source_code_path)) as f:
                if(source_code_path.suffix in [".c", ".h"]):
                    parser=tree_sitter.Parser(C_LANGUAGE)
                    source_code_bytes=f.read()
                    global oldTreeC
                    oldTreeC=parser.parse(source_code_bytes.encode(), oldTreeC)
                    toReturnObject["content"]=get_file_outline_helper(oldTreeC, C_LANGUAGE)
                    return json.dumps(toReturnObject)
                elif(source_code_path.suffix in [".cpp", ".hpp"]):
                    parser=tree_sitter.Parser(CPP_LANGUAGE)
                    source_code_bytes=f.read()
                    global oldTreeCPP
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
                    
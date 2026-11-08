import tree_sitter

def execute_query(language, root_node, query_source, capture_name):
    query=tree_sitter.Query(language, query_source)
    cursor = tree_sitter.QueryCursor(query)

    captures = cursor.captures(root_node)

    return captures.get(capture_name, [])

def get_file_outline_helper(parse_tree:tree_sitter.Tree,language:tree_sitter.Language, include_functions:bool=True, include_types:bool=True, include_macros:bool=True, include_globals:bool=False)->dict:
    list_data={}
    if include_functions:
        list_data["functions"]=[]
        functions=execute_query(language,parse_tree.root_node, "(function_definition) @function", "function")
        for function in functions:
            list_data.append(
                {
                    "type":"function",
                    "info":function.text.decode("utf-8")
                }
            )
    if include_types:
        structs=execute_query(language, parse_tree.root_node, "(struct_specifier) @struct","struct")
        for struct in structs:
            list_data.append(
                {
                    "type":"struct",
                    "info":struct.text.decode("utf-8")
                }
            )
        unions=execute_query(language, parse_tree.root_node, "(union_specifier) @union", "union")
        for union in unions:
            list_data.append(
                {
                    "type":"union",
                    "info":union.text.decode("utf-8")
                }
            )
        enums=execute_query(language, parse_tree.root_node, "(enum_specifier) @enum", "enum")
        for enum in enums:
            list_data.append(
                {
                    "type":"enum",
                    "info":enum.text.decode("utf-8")
                }
            )
        primitives=execute_query(language, parse_tree.root_node, "(primitive_type) @primitive_type", "primitive_type")
        for primitive in primitives:
            list_data.append(
                {
                    "type":"primitve",
                    "info":primitive.text.decode("utf-8")
                }
            )
        type_definitions=execute_query(language, parse_tree.root_node, "(type_definition) @type_definition" , "type_definition")
        for type_definition in type_definitions:
            list_data.append(
                {
                    "type":"type_definition",
                    "info":type_definition.text.decode("utf-8")
                }
            )

    if include_globals:
        global_capture_query="""(translation_unit
                    (declaration
                            declarator: [
                                (identifier) @global_variable
                                (init_declarator
                                    declarator: (identifier) @global_variable
                                )
                            ]
                        )
                    )"""
        global_captures=execute_query(language, parse_tree.root_node, global_capture_query, "global_variable")
        for global_capture in global_captures:
            list_data.append(
                {
                    "type":"global_identifier",
                    "info":global_capture.text.decode("utf-8")
                }
            )

    if include_macros:
        macro_capture_query="""[
        (preproc_def) @macro
        (preproc_function_def) @macro
        ]"""
        macros=execute_query(language, parse_tree.root_node, macro_capture_query, "macro")
        for macro in macros:
            list_data.append(
                {
                    "type":"macro",
                    "info":macro.text.decode("utf-8")
                }
            )

    return list_data
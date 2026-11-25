import tree_sitter
import re

def execute_query(language, root_node, query_source, capture_name):
    query=tree_sitter.Query(language, query_source)
    cursor = tree_sitter.QueryCursor(query)

    captures = cursor.captures(root_node)

    return captures.get(capture_name, [])


def extract_cpp_classes(root_node):
    """
    Extract C++ classes and structs.

    Args:
        language: Tree-sitter C++ Language object.
        root_node: parse_tree.root_node.

    Returns:
        List of dictionaries containing class information.
    """

    classes = []

    def get_text(node):
        return node.text.decode("utf-8", errors="replace") if node else ""

    def descendants(node):
        """Yield node and all its descendants."""
        yield node
        for child in node.children:
            yield from descendants(child)

    def find_child(node, node_type):
        for child in node.children:
            if child.type == node_type:
                return child
        return None

    def get_name(node):
        name_node = node.child_by_field_name("name")

        if name_node:
            return get_text(name_node)

        # Fallback for grammar variations.
        for child in node.named_children:
            if child.type in ("type_identifier", "identifier"):
                return get_text(child)

        return None

    def get_declarator_name(node):
        """
        Extract the identifier from a field or function declarator.
        """

        if node is None:
            return None

        identifiers = []

        valid_types = {
            "identifier",
            "field_identifier",
            "type_identifier",
            "operator_name",
            "destructor_name"
        }

        for child in descendants(node):
            if child.type in valid_types and not child.children:
                identifiers.append(get_text(child))

        return identifiers[-1] if identifiers else None

    def get_member_name(node, is_method):
        target_type = (
            "function_declarator"
            if is_method else "field_declarator"
        )

        candidates = [
            child for child in descendants(node)
            if child.type == target_type
        ]

        if not candidates:
            return None

        declarator = candidates[0].child_by_field_name("declarator")

        if declarator is None:
            declarator = candidates[0]

        return get_declarator_name(declarator)

    def get_access(node, default_access):
        text = get_text(node).strip()

        if text in ("public", "private", "protected"):
            return text

        return default_access

    def extract_bases(node, default_access):
        bases = []

        base_clause = find_child(node, "base_class_clause")

        if not base_clause:
            return bases

        for child in base_clause.named_children:

            if child.type != "base_class_specifier":
                continue

            signature = get_text(child).strip()

            access_match = re.search(
                r"\b(public|private|protected)\b",
                signature
            )

            access = (
                access_match.group(1)
                if access_match else default_access
            )

            base_name = re.sub(
                r"\b(public|private|protected|virtual)\b",
                "",
                signature
            ).strip()

            bases.append({
                "name": base_name,
                "access": access
            })

        return bases

    def extract_members(class_body, default_access):

        members = []
        current_access = default_access

        if class_body is None:
            return members

        for child in class_body.named_children:

            node_type = child.type

            # Ignore comments.
            if node_type == "comment":
                continue

            # Track current access specifier.
            if node_type == "access_specifier":
                current_access = get_access(
                    child, current_access
                )
                continue

            # Member function declaration or data declaration.
            if node_type == "field_declaration":

                is_method = any(
                    n.type == "function_declarator"
                    for n in descendants(child)
                )

                members.append({
                    "name": get_member_name(child, is_method),
                    "kind": "method" if is_method else "field",
                    "access": current_access,
                    "signature": get_text(child).strip()
                })

            # Inline method definition.
            elif node_type == "function_definition":

                members.append({
                    "name": get_member_name(child, True),
                    "kind": "method",
                    "access": current_access,
                    "signature": get_text(child).strip()
                })

            # Preserve declarations not yet supported.
            else:
                members.append({
                    "name": None,
                    "kind": "other",
                    "access": current_access,
                    "signature": get_text(child).strip()
                })

        return members

    # Collect class and struct nodes.
    class_nodes = []

    def traverse(node):
        if node.type in ("class_specifier", "struct_specifier"):
            class_nodes.append(node)

        for child in node.children:
            traverse(child)

    traverse(root_node)

    for node in class_nodes:

        source = get_text(node).strip()

        kind_match = re.match(r"(class|struct|union)\b", source)

        if not kind_match:
            continue

        kind = kind_match.group(1)
        name = get_name(node)

        if not name:
            continue

        default_access = (
            "public" if kind in ("struct", "union")
            else "private"
        )

        class_body = find_child(node, "field_declaration_list")

        classes.append({
            "name": name,
            "kind": kind,
            "is_forward_declaration": class_body is None,
            "bases": extract_bases(node, default_access),
            "members": extract_members(
                class_body, default_access
            )
        })

    return classes


def get_functions(language:tree_sitter.Language, root_node)->list:
    querySource="(function_definition)@function"
    captures=execute_query(language, root_node, querySource, "function")

    functions=[]

    for capture in captures:
        return_type_node=capture.child_by_field_name("type")
        func={}
        for storage_class_node in capture.named_children:
            if storage_class_node.type=="storage_class_specifier":
                func["storage_class"]=storage_class_node.text.decode()
        func["return_type"]=return_type_node.text.decode()
        declarator_node=capture.child_by_field_name("declarator")
        while(declarator_node.type!="function_declarator"):
            declarator_node=declarator_node.child_by_field_name("declarator")
        for node in declarator_node.named_children:
            if node.type=="identifier":
                func["function_name"]=node.text.decode()
        parameter_list_node=declarator_node.child_by_field_name("parameters")
        func["parameters"]=[]
        if parameter_list_node is not None:
            for node in parameter_list_node.named_children:
                if node.type=="parameter_declaration":
                    func["parameters"].append(node.text.decode())
        functions.append(func)

    return functions

def parse_struct(struct_node):

    name_node = struct_node.child_by_field_name("name")
    body_node = struct_node.child_by_field_name("body")

    struct = {
            "name": name_node.text.decode() if name_node else None,
            "attributes": []
    }

    if body_node is None:
        return struct

    for field_node in body_node.named_children:

        if field_node.type != "field_declaration":
            continue

        type_node = field_node.child_by_field_name("type")
        declarator_node = field_node.child_by_field_name("declarator")

        attribute = {
            "declaration": field_node.text.decode()
        }

        if declarator_node:
            attribute["declarator"] = declarator_node.text.decode()

        if type_node and type_node.type == "struct_specifier":

            nested_name = type_node.child_by_field_name("name")

            attribute["type"] = (
                "struct " + nested_name.text.decode()
                if nested_name else "anonymous struct"
            )

            attribute["nested_struct"] = parse_struct(type_node)

        struct["attributes"].append(attribute)

    return struct

def get_structs(language: tree_sitter.Language, root_node)->list:
    querySourceStruct="(struct_specifier)@struct"
    queryStruct=tree_sitter.Query(language, querySourceStruct)
    queryStructCursor=tree_sitter.QueryCursor(queryStruct)

    structCapture=queryStructCursor.captures(root_node)

    structs=[]

    for capture in structCapture.get("struct", []):
        parent=capture.parent

        nested=False

        while parent is not None:
            if parent.type=="struct_specifier":
                nested=True
                break
            parent=parent.parent  

        if not nested:
            structs.append(parse_struct(capture))

    return structs

def get_unions(language: tree_sitter.Language, root_node)->list:
    querySourceUnion="(union_specifier)@union"
    queryUnion=tree_sitter.Query(language, querySourceUnion)
    queryUnionCursor=tree_sitter.QueryCursor(queryUnion)
    queryCapture=queryUnionCursor.captures(root_node)

    def parse_union(union_node):
        name_node=union_node.child_by_field_name("name")
        body_node=union_node.child_by_field_name("body")
        union={
            "name": name_node.text.decode() if name_node is not None else "Anonymous",
            "attributes":[]
        }
        if body_node is None:
            return union

        for field_node in body_node.named_children:
            if field_node.type!="field_declaration":
                continue

            type_node=field_node.child_by_field_name("type")
            declaration_node=field_node.child_by_field_name("declarator")
            attribute={
                "declaration":field_node.text.decode()
            }
            if declaration_node:
                attribute["declarator"]=declaration_node.text.decode()

            if type_node and type_node.type=="struct_specifier":
                attribute["struct_details"]=parse_struct(type_node)
            elif type_node and type_node.type=="union_specifier":
                nested_name=field_node.child_by_field_name("name")
                attribute["type"]=(
                    "union "+ nested_name.text.decode() if nested_name else "Anonymous"
                )
                attribute["union_details"]=parse_union(type_node)
            union["attributes"].append(attribute)

        return union


    unions=[]
    for capture in queryCapture.get("union", []):
        print(capture)
        nested=False
        parent=capture.parent
        while parent is not None:
            if parent.type=="union_specifier":
                nested=True
                break
            parent=parent.parent
        if not nested:
            unions.append(parse_union(capture))

    return unions

def get_enums(language:tree_sitter.Language, root_node)->list:
    enums=[]
    enumCaptures=execute_query(language, root_node, "(enum_specifier)@enum", "enum")
    for enumCapture in enumCaptures:
        enum_name_node=enumCapture.child_by_field_name("name")
        enum={
             "name":enum_name_node.text.decode() if enum_name_node is not None else "Anonymous Enum"
        }
        parent_node=enumCapture.parent
        if parent_node is not None and parent_node.type == "type_definition":

            # Extract the typedef declarator
            declarator_node = parent_node.child_by_field_name("declarator")

            if declarator_node is not None:
                enum["typedef_name"] = declarator_node.text.decode()
        body_node=enumCapture.child_by_field_name("body")
        enum["constants"]=[]
        if body_node is not None:
            for body_node_child in body_node.named_children:
                if body_node_child.type=="enumerator":
                    enum["constants"].append(body_node_child.text.decode())

        enums.append(enum)
    return enums

def get_typedefs_primitives(language: tree_sitter.Language, root_node)->list:
    typedefs = []
    typedefCaptures=execute_query(language, root_node, "(type_definition)@typedef", "typedef")
    for typedef_node in typedefCaptures:

        type_node = typedef_node.child_by_field_name("type")
        declarator_node = typedef_node.child_by_field_name("declarator")

        if type_node is None or declarator_node is None:
            continue

        # Exclude struct, union and enum typedefs
        if any(child.type in (
        "struct_specifier",
        "union_specifier",
        "enum_specifier"
    ) for child in type_node.named_children):
            continue

        typedefs.append({
        "name": declarator_node.text.decode(),
        "type": type_node.text.decode()
    })
    return typedefs

def get_macros(language: tree_sitter.Language, root_node)->list:
    query_source = """
  (preproc_def) @object_macro
  (preproc_function_def) @function_macro
  """
    query = tree_sitter.Query(language, query_source)
    cursor = tree_sitter.QueryCursor(query)
    captures = cursor.captures(root_node)

    object_macros=[]

    for node in captures.get("object_macro", []):
        object_macro={}
        name_node=node.child_by_field_name("name")
        object_macro["name"]=(name_node.text.decode() if name_node else "Anonymous Macro")
        value_node=node.child_by_field_name("value")
        object_macro["value"]=(value_node.text.decode() if value_node else "NULL")
        object_macros.append(object_macro)

    function_macros=[]

    for node in captures.get("function_macro", []):
        name_node=node.child_by_field_name("name")
        func_macro={
            "name":(name_node.text.decode() if name_node else "Anonymous function macro")
        }
        func_macro["parameter_list"]=[]
        param_node=node.child_by_field_name("parameters")
        for param_child_node in param_node.named_children:
            if param_child_node.type=="identifier":
                func_macro["parameter_list"].append(param_child_node.text.decode())

        value_node=node.child_by_field_name("value")
        func_macro["definition"]=(value_node.text.decode() if value_node else "NULL")
        function_macros.append(func_macro)

    return object_macros+function_macros

def get_file_outline_helper(parse_tree:tree_sitter.Tree,language:tree_sitter.Language, include_functions:bool=True, include_types:bool=True, include_macros:bool=True)->dict:
    list_data={}
    if include_functions:
        list_data["functions"]=get_functions(language, parse_tree.root_node)
    if include_types:
        list_data["structs"]=get_structs(language, parse_tree.root_node)
        list_data["unions"]=get_unions(language, parse_tree.root_node)
        list_data["enums"]=get_enums(language, parse_tree.root_node)
        list_data["typedefs"]=get_typedefs_primitives(language, parse_tree.root_node)
    if include_macros:
        list_data["macros"]=get_macros(language, parse_tree.root_node)

    return list_data
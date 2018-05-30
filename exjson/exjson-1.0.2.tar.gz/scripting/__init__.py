from scripting import extensions

_REF_PREFIXES = ['$this.', '$parent.', '$root.']


def parse(source, raise_error_on_invalid_value=False):
    if "$." not in source:
        return _parse_reference_calls(source)
    calls = {}
    updated_source = source
    for line in source.splitlines():
        c = 0
        while c < len(line):
            if line[c] == "$":
                call_close = c + 1
                call_params = ""
                while line[call_close] == ".":
                    call_close = line.find(")", call_close + 1) + 1
                if call_close > 0:
                    func_call = line[c:call_close]
                    calls[func_call] = extensions.get_function(func_call)
                    c += call_close
            c += 1
    for fn_key in calls.keys():
        if hasattr(calls[fn_key][0], "_isolated_instance_execution") and calls[fn_key][0]._isolated_instance_execution:
            i = 0
            new_updated_source = ""
            for call_instance in updated_source.split(fn_key):
                if i == 0:
                    updated_instance = call_instance
                else:
                    updated_instance = str(calls[fn_key][0](*calls[fn_key][1])) + call_instance
                new_updated_source += updated_instance
                i += 1
            updated_source = new_updated_source
            # Call Close Function for the Extension call
            if hasattr(calls[fn_key][0], "_close") and calls[fn_key][0]._close is not None:
                calls[fn_key][0]._close()
        else:
            updated_source = updated_source.replace(fn_key, str(calls[fn_key][0](*calls[fn_key][1])))
    # Parse Reference Calls
    updated_source = _parse_reference_calls(updated_source)
    # Result
    return updated_source


def _parse_reference_calls(source: str):
    """Parses reference calls"""
    if _has_reference_calls(source):
        updated_source = source
        # Extract Source Tree and Reference Tree
        base = _extract_tree(updated_source)
        # Source Tree
        source_tree = base[0]
        # References
        ref_calls = base[1]
        # Reference Tree
        ref_tree = base[2]
        if ref_calls is not None and len(ref_calls) > 0:
            for r in ref_calls:
                updated_source = updated_source.replace(r, source_tree[ref_calls[r]])
                # Update Tree when a value ref_call is updated. This guarantees references of references to get the initially referenced value.
                source_tree = _extract_tree(updated_source, extract_ref_calls=False)[0]
        return updated_source
    else:
        return source

def _has_reference_calls(source:str):
    if source is not None and ("$root." in source or "$this." in source or "$parent" in source):
        return True
    else:
        return False


def _extract_tree(source: str, parent: str = None, outer_tree: dict = None, extract_ref_calls: bool = True):
    tree = {}
    if outer_tree is not None:
        tree = { **outer_tree }
    ref_list = {}
    ref_tree = {}
    i = 0
    done = False
    working_source = source
    while not done:
        # Done
        if i == len(working_source):
            done = True
            continue
        src_char = working_source[i]
        if src_char in [' ', '\n', '\t']:
            i = i + 1
            continue
        # Find property assignments
        elif src_char == ":":
            source_key_scope = working_source[:i]
            try:
                source_key_start_index = source_key_scope.rindex(',')
            except:
                source_key_start_index = source_key_scope.rindex("{")
            source_key = source_key_scope[source_key_start_index:].replace('"', '').replace(' ', '').replace('\t',
                                                                                                             '').replace(
                '\n', '').replace('{', '').replace(',', '')
            if parent is not None and parent != "":
                source_key = f"{parent}.{source_key}"
            source_value_scope = working_source[i:]
            # Find arrays
            if source_value_scope.replace(' ', '').replace('\t', '')[1] == '[':
                source_value_end_index = source_value_scope.index("]") + 1
            elif source_value_scope.replace(' ', '').replace('\t', '')[1] == "{":
                source_value_end_index = source_value_scope.index("}") + 1
            else:
                try:
                    source_value_end_index = source_value_scope.index(",")
                except:
                    source_value_end_index = source_value_scope.index("}")
            source_value = source_value_scope[1:source_value_end_index].strip(' ').strip('\t').strip('\n').strip('"')
            # Process Object
            if source_value[0] == "{" and source_value[-1] == "}":
                inner_object_tree = _extract_tree(source_value, source_key, tree)
                for inner_object_key in inner_object_tree[0]:
                    full_key = f"{source_key}.{inner_object_key.replace(source_key, '')}".replace("..", ".")
                    tree[full_key] = inner_object_tree[0][inner_object_key]
                    # Reference Tree
                    ref_tree[full_key] = _get_abs_ref_tree_entry(full_key, source_key)
                    # Extract Ref Calls
                    if extract_ref_calls:
                        if inner_object_tree[1] is not None:
                            for k in inner_object_tree[1]:
                                if k not in ref_list:
                                    ref_list[k] = inner_object_tree[1][k]
            # Set the Value
            tree[source_key] = source_value
            # Reference tree
            ref_tree[source_key] = _get_abs_ref_tree_entry(source_key, parent)
            # Extract References
            if extract_ref_calls:
                tree_keys = [k for k in tree.keys()]
                ref_call = _extract_ref_call(source_value, tree_keys, source_key)
                ref_call = _get_abs_ref_call_from_ref_tree(ref_tree, ref_call)
                if ref_call is not None:
                    if ref_call[5] in tree_keys:
                        if ref_call[0] not in ref_list:
                            ref_list[ref_call[0]] = ref_call[5]
                    else:
                        # TODO: Review incremental key verification
                        i = 0
                        found = False
                        ref_call_base = ref_call[5]
                        ref_call_temp = ref_call_base
                        while True:
                            if i > len(ref_call_base):
                                break
                            if ref_call_temp in tree_keys:
                                found = True
                                break
                            ref_call_temp = ref_call_base[:i]
                            i = i + 1
                        if found:
                            ref_call_new = ()
                            for r in range(0, len(ref_call)):
                                ref_call_new_value = ref_call[r]
                                if r == 5:
                                    ref_call_new_value = ref_call_temp
                                else:
                                    ref_call_last_element_index = -1
                                    ref_call_elements = ref_call_temp.split('.')
                                    ref_call_last_element = ref_call_elements[-1]
                                    if len(ref_call_elements) > 1:
                                        try:
                                            ref_call_last_element_index = ref_call[r].index(ref_call_last_element)
                                        except:
                                            pass
                                        if ref_call_last_element_index > 0:
                                            ref_call_last_element_index = ref_call_last_element_index + len(ref_call_last_element)
                                        ref_call_new_value = ref_call[r][:ref_call_last_element_index]
                                    else:
                                        ref_call_new_value = ref_call[r]
                                ref_call_new = ref_call_new + (ref_call_new_value,)
                            if ref_call_new[0] not in ref_list:
                                ref_list[ref_call_new[0]] = ref_call_temp

            # Reset
            working_source = working_source[i + source_value_end_index:]
            i = 0
            continue
        # Next Character
        i = i + 1
    return (tree, ref_list, ref_tree)


def _extract_ref_call(source: str, keys: list, caller:str):
    if _has_reference_calls(source):
        ref_call_without_prefix = ""
        ref_start_index = source.index("$")
        working_source = source[ref_start_index:].replace('"', "").strip(' ')
        try:
            ref_prefix_end = working_source.index(".")
        except:
            return None
        ref_call_prefix = working_source[:ref_prefix_end]
        working_source = working_source[ref_prefix_end + 1:]
        i = 0
        while i < len(working_source):
            if working_source[i] in ['"', '\n', '\t', ' ', '$', '}', ']', ',', '|']:
                break
            ref_call_without_prefix = ref_call_without_prefix + working_source[i]
            if ref_call_without_prefix in keys:
                break
            i = i + 1
        if ref_call_prefix != "" and ref_call_without_prefix != "":
            ref_call = f"{ref_call_prefix}.{ref_call_without_prefix}"
            return (ref_call, ref_call_without_prefix, ref_call_prefix, caller)
        else:
            return None
    else:
        return None


def _get_abs_ref_tree_entry(source_key: str, parent_key: str):
    """Get Absolute path to reference prefixes"""
    this = source_key
    parent = parent_key
    if '.' in source_key:
        this = '.'.join(source_key.split(".")[:-1])
        parent = '.'.join(source_key.split(".")[:-2])
        if parent != "" and parent[-1] == ".":
            parent = parent[:-1]
    return {
        "parent": parent,
        "this": this
    }

def _get_abs_ref_call_from_ref_tree(ref_tree:dict, ref_call:tuple):
    if ref_tree is not None and ref_call is not None:
        if '$this' in ref_call[2]:
            return ref_call + (ref_tree[ref_call[3]]["this"], f"{ref_tree[ref_call[3]]['this']}.{ref_call[1]}")
        elif '$parent' in ref_call[2]:
            return ref_call + (ref_tree[ref_call[3]]["this"], f"{ref_tree[ref_call[3]]['parent']}.{ref_call[1]}")
        else:
            return ref_call + (ref_call[1],ref_call[1])
    else:
        if ref_call is not None:
            return ref_call + (ref_call[1],ref_call[1])
        else:
            return None

import os
import re
from collections import defaultdict

import polib
from ruamel import yaml

from publisher import settings


def build_translation_template(output_file):
    translatable_strings = get_translatable_strings()
    build_pot_file(translatable_strings, output_file)


def build_pot_file(strings, output_file):
    pot = polib.POFile()
    for string, locations in strings.items():
        entry = polib.POEntry(msgid=string, occurrences=locations)
        pot.append(entry)

    pot.save(fpath=output_file)


def get_translatable_strings():

    results = defaultdict(list)
    content_map = get_content_map()

    for yaml_file in get_procedure_yaml_files():
        with open(yaml_file, 'rb') as f:
            yaml_obj = yaml.load(f, Loader=yaml.RoundTripLoader)

        strings = extract_content(yaml_obj, content_map)
        for i in range(len(strings)):
            results[strings[i]].append((yaml_file, i))

    return results


def get_content_map():

    return {
        'name': str,
        'cta_text': str,
        'title': str,
        'subtitle': str,
        'sub_title': str,
        'text': str,
        'content': str,
        'answer': str,
        'desc': str,
        'numbered_list': list,
        'list': list,
        'choices': list,
    }


def extract_content(yaml_obj, content_map):
    results = []
    if isinstance(yaml_obj, list):
        for v in yaml_obj:
            results += extract_content(v, content_map)
    elif isinstance(yaml_obj, dict):
        for k, v in yaml_obj.items():
            mapped_type = content_map.get(k.lower())
            value_matches_type = mapped_type is not None and isinstance(v, mapped_type)
            if value_matches_type:
                string_list = v if mapped_type == list else [v]
                results += [s for s in string_list if is_translatable(s)]
            else:
                results += extract_content(v, content_map)

    return results


def is_translatable(s):
    is_not_empty = s is not None and s.strip() != ''
    return is_not_empty and (' ' in s or not re.search(r'[\d_]', s))


def get_procedure_yaml_files():

    yaml_files = []
    for subdir, dirs, files in os.walk(settings.PROCEDURE_CHECKOUT_DIRECTORY):
        yaml_files += [os.path.join(subdir, f) for f in files if f.endswith('.yml')]

    return yaml_files

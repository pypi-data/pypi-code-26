import sys
import collections
import yaml
import yschema


def validate_dictionaries(schema, documents, schema_name, doc_names):
    """
    Validate the given documents (list of dicts) against the schema (a
    dictionary). This function returns 0 on success and the number of
    failed documents on (partial) failure. Returns -1 if the schema is not
    valid (for some subset of schema problems).
    """
    print('YSchema is reading schema', schema_name)
    indent = '  '
    prefix1 = indent + 'ERROR: '
    prefix2 = ' ' * len(prefix1)
    try:
        schema = yschema.Schema(schema)
        print(indent + 'OK')
    except Exception as e:
        print(indent + 'Invalid schema!')
        print(indent + str(e).replace('\n', '\n' + indent))
        return -1

    num_errors = 0
    for doc, name in zip(documents, doc_names):
        print('Validating document', name)
        errors = schema.validate(doc)
        if errors:
            for e in errors:
                print(prefix1 + e.replace('\n', '\n' + prefix2))
            num_errors += 1
        else:
            print('  OK')
    return num_errors


def run_from_console():
    """
    Parse command line arguments and then run the validator
    """
    import argparse
    afile = argparse.FileType(mode='rt', encoding='utf8')
    parser = argparse.ArgumentParser(prog='YSchema',
                                     description='YAML schema validator')
    parser.add_argument('schemafile', help='Name of the file containing the '
                        'YSchema definition', type=afile)
    parser.add_argument('datafiles', help='Name of the file(s) containing data '
                        'to be validated', nargs='+', type=afile)
    args = parser.parse_args()

    # Ensure YAML reads data in an ordered way
    yaml.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
                         lambda loader, node: collections.OrderedDict(loader.construct_pairs(node)))

    # Read the YAML files
    schema = yaml.safe_load(args.schemafile)
    documents = [yaml.safe_load(datafile) for datafile in args.datafiles]
    document_names = [datafile.name for datafile in args.datafiles]

    # Run the validation
    return validate_dictionaries(schema, documents, args.schemafile.name,
                                 document_names)


if __name__ == '__main__':
    sys.exit(run_from_console())

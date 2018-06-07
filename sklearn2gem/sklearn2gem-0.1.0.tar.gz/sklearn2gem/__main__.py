import sys

from sklearn2gem import SklearnGemGenerator

def main(argv):
    try:
        name, pkl_path, dest_path = argv[1:]
    except:
        print(f'Usage: {argv[0]} <gem name>@<version> <pickle file> <destination>')
        return 1

    lib_name, version = name.split('@')
    generator = SklearnGemGenerator(lib_name, version, pkl_path)
    generator.generate(dest_path)
    return 0

sys.exit(main(sys.argv))

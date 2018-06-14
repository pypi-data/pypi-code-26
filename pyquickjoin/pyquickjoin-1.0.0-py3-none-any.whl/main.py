import sys
import argparse

from . import join_dict, join_bsddb

def main(args=None):
    if args == None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description='Join two files quickly')

    parser.add_argument('-1', metavar='FIELD', dest="file1_key_column", type=int, default=1, help='join on this FIELD of file 1')
    parser.add_argument('-2', metavar='FIELD', dest="file2_key_column", type=int, default=1, help='join on this FIELD of file 2')
    parser.add_argument('-t', metavar='CHAR', dest="separator", default="\t", help='use CHAR as input and output field separator')
    parser.add_argument('-d', '--disk', action='store_true')
    parser.add_argument('file1', metavar='FILE1')
    parser.add_argument('file2', metavar='FILE2', nargs='?', default="-")

    parsed_args = parser.parse_args(args)

    if len(parsed_args.separator) != 1:
        parser.error("separator CHAR must be exactly 1 character")

    if parsed_args.file1 == "-" and parsed_args.file2 == "-" :
        parser.error("both files cannot be standard input")

    file1 = argparse.FileType('r')(parsed_args.file1)
    file2 = argparse.FileType('r')(parsed_args.file2)

    if parsed_args.disk:
        join_method = join_bsddb
    else:
        join_method = join_dict

    joined = join_method(
        file1,
        parsed_args.file1_key_column - 1,
        file2,
        parsed_args.file2_key_column - 1,
        parsed_args.separator)

    for line in joined:
        print(line)

if __name__ == "__main__":
    main()

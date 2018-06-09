import core
import argparse

ap = argparse.ArgumentParser()

ap.add_argument("-f", "--file", required=True, help="Target file")
ap.add_argument("-s", "--save", required=False, help="Output file")

args = vars(ap.parse_args())

document = core.DocumentParser(args['file'])

if args['save'] == None:
    document.read()

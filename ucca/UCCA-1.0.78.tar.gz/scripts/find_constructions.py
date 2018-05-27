from argparse import ArgumentParser

from tqdm import tqdm

from ucca import constructions
from ucca.ioutil import get_passages_with_progress_bar


def main(args):
    for passage in get_passages_with_progress_bar(args.passages):
        extracted = constructions.extract_edges(passage, constructions=args.constructions, verbose=args.verbose)
        if any(extracted.values()):
            with tqdm.external_write_mode():
                if not args.verbose:
                    print("%s:" % passage.ID)
                for construction, edges in extracted.items():
                    if edges:
                        print("  %s:" % construction.description)
                        for edge in edges:
                            print("    %s [%s %s]" % (edge, edge.tag, edge.child))
                print()


if __name__ == "__main__":
    argparser = ArgumentParser(description="Extract linguistic constructions from UCCA corpus.")
    argparser.add_argument("passages", nargs="+", help="the corpus, given as xml/pickle file names")
    constructions.add_argument(argparser, False)
    argparser.add_argument("-v", "--verbose", action="store_true", help="print tagged text for each passage")
    main(argparser.parse_args())

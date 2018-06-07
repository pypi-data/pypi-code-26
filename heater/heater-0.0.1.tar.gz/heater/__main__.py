import argparse
import csv
import sys

from .heater import make_heatmap


def parse_args():
    parser = argparse.ArgumentParser(description="Create a heatmap on top of a base image.")
    parser.add_argument(
        "background_file",
        type=argparse.FileType(mode="rb"),
        help="the image to use as a background",
    )
    parser.add_argument(
        "coords_file",
        type=argparse.FileType(mode="r"),
        help="a CSV of x and y positions",
    )
    parser.add_argument(
        "output_file",
        type=argparse.FileType(mode="wb"),
        help="the name of the output file",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    points = [(int(x), int(y)) for x, y in csv.reader(args.coords_file)]
    heatmap = make_heatmap(args.background_file, points)
    heatmap.save(args.output_file)
    return 0


if __name__ == "__main__":
    sys.exit(main())

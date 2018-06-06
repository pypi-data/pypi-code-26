"""
This is the command-line interface for the NTCIR Math density estimator package.
"""

from argparse import ArgumentParser
import gzip
import logging
from logging import getLogger
from pathlib import Path
import pickle
from sys import stdout

from numpy import linspace

from .estimator import get_judged_identifiers, get_all_positions, get_estimators, get_estimates
from .view import plot_estimates


ESTIMATORS_PATH = Path("estimators.pkl.gz")
LOG_PATH = Path("__main__.log")
LOG_FORMAT = "%(asctime)s : %(levelname)s : %(message)s"
LOGGER = getLogger(__name__)
MIN_RELEVANT_SCORE = 2
ROOT_LOGGER = getLogger()
SAMPLING_FREQUENCY = 1000


class LabelledPath(object):
    """This class represents a path labelled with a unique single-letter label.

    Parameters
    ----------
    label : str
        A single-letter label.
    path : Path
        The labelled-path.

    Attributes
    ----------
    labels : dict of (str, Path)
        A mapping between labels, and paths.
    label : str
        A single-letter label.
    path : Path
        The labelled-path.
    """
    labels = dict()

    def __init__(self, label, path):
        assert isinstance(label, str) and len(label) == 1
        assert label not in LabelledPath.labels
        assert isinstance(path, Path)
        self.label = label
        self.path = path
        LabelledPath.labels[self.label] = self.path


def main():
    """ Main entry point of the app """
    ROOT_LOGGER.setLevel(logging.DEBUG)

    file_handler = logging.StreamHandler(LOG_PATH.open("wt"))
    formatter = logging.Formatter(LOG_FORMAT)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    ROOT_LOGGER.addHandler(file_handler)

    terminal_handler = logging.StreamHandler(stdout)
    terminal_handler.setFormatter(formatter)
    terminal_handler.setLevel(logging.INFO)
    ROOT_LOGGER.addHandler(terminal_handler)

    LOGGER.debug("Parsing command-line arguments")
    parser = ArgumentParser(
        description="""
            Use NTCIR-10 Math, NTCIR-11 Math-2, and NTCIR-12 MathIR datasets to compute density, and
            probability estimators.
        """)
    parser.add_argument(
        "--datasets", nargs='+', required=False,
        type=lambda s: LabelledPath(s.split('=', 1)[0], Path(s.split('=', 1)[1])), help="""
            Paths to the directories containing the datasets. Each path must be prefixed with a
            unique single-letter label (e.g. "A=/some/path"). Note that all the datasets must be in
            the NTCIR-11 Math-2, and NTCIR-12 MathIR format, even the NTCIR-10 Math dataset.
        """)
    parser.add_argument(
        "--judgements", nargs='+', required=False,
        type=lambda s: (LabelledPath.labels[s.split(':', 1)[0]], Path(s.split(':', 1)[1])), help="""
            Paths to the files containing relevance judgements. Each path must be prefixed with
            single-letter labels corresponding to the judged datasets (e.g.
            "A:/some/path/judgement.dat"). Note that all the judgements must be in the NTCIR-11
            Math-2, and NTCIR-12 MathIR format, even the NTCIR-10 Math dataset judgements.
        """)
    parser.add_argument(
        "--plots", type=Path, nargs='+', help="""
            The path to the files, where the probability estimators will plotted. When no datasets
            are specified, the estimators file will be loaded.
        """)
    parser.add_argument(
        "--estimators", type=Path, default=ESTIMATORS_PATH, help="""
            The path to the file, where the density, and probability estimators will be stored. When
            no datasets are specified, this file will be loaded to provide the estimators for
            plotting. Defaults to %(default)s.
        """)
    parser.add_argument(
        "--num-workers", type=int, default=1, help="""
            The number of processes that will be used for processing the NTCIR-10 Math dataset, and
            for computing the density, and probability estimates. Defaults to %(default)d.
        """)
    args = parser.parse_args()

    LOGGER.debug("Performing sanity checks on the command-line arguments")
    if args.datasets:
        for dataset in args.datasets:
            assert dataset.path.exists() and dataset.path.is_dir(), \
                "Dataset %s does not exist" % dataset.path
        assert args.judgements, "No relevance judgements were specified for the datasets"
        for _, judgement_path in args.judgements:
            assert judgement_path.exists() and judgement_path.is_file(), \
                "Relevance judgement %s does not exist" % judgement_path
        assert not args.estimators.exists() or args.estimators.is_file(), \
            "File %s, where estimators are to be stored, is non-regular." % args.estimators
        if args.estimators.exists():
            LOGGER.warning("%s exists", args.estimators.name)
    if args.plots:
        assert args.datasets or args.estimators, \
            "Neither datasets, not a stored file with estimators was provided as a plot source"
        if not args.datasets:
            assert args.estimators.exists() and args.estimators.is_file(), \
                "The file %s with estimators does not exist" % args.estimators
        for plot in args.plots:
            assert plot.parents[0].exists() and plot.parents[0].is_dir(), \
                "Directory %s, where a plot is to be stored, does not exist" % \
                args.estimators.parents[0]
            if plot.exists():
                LOGGER.warning("%s exists", plot)
    assert args.estimators.parents[0].exists() and args.estimators.parents[0].is_dir(), \
        "Directory %s, where the estimators are to be stored, does not exist" % \
        args.estimators.parents[0]
    assert args.num_workers > 0, "The number of workers must be non-negative"

    if args.datasets:
        identifiers_judged = {}
        identifiers_relevant = {}
        for dataset_path, judgement_path in args.judgements:
            LOGGER.info(
                "Retrieving judged paragraph identifiers, and scores from %s", judgement_path.name)
            if dataset_path not in identifiers_judged:
                identifiers_judged[dataset_path] = set()
            if dataset_path not in identifiers_relevant:
                identifiers_relevant[dataset_path] = set()
            with judgement_path.open("rt") as f:
                for identifier, score in get_judged_identifiers(f):
                    identifiers_judged[dataset_path].add(identifier)
                    if score >= MIN_RELEVANT_SCORE:
                        identifiers_relevant[dataset_path].add(identifier)

        identifiers_all = {}
        positions_all = {}
        positions_relevant = {}
        for dataset in args.datasets:
            LOGGER.info(
                "Retrieving all paragraph identifiers, and positions from %s", dataset.path.name)
            identifiers_all[dataset.path] = []
            positions_all[dataset.path] = []
            positions_relevant[dataset.path] = []
            for directory, identifier, position in get_all_positions(dataset.path, args.num_workers):
                identifiers_all[dataset.path].append((directory, identifier))
                positions_all[dataset.path].append(position)
                if identifier in identifiers_relevant[dataset.path]:
                    positions_relevant[dataset.path].append(position)

        for dataset in args.datasets:
            LOGGER.info(
                "%d / %d / %d relevant / judged / total identifiers in dataset %s",
                len(identifiers_relevant[dataset.path]), len(identifiers_judged[dataset.path]),
                len(identifiers_all[dataset.path]), dataset.path.name)

        LOGGER.info("Fitting density, and probability estimators")
        estimators = get_estimators(positions_all, positions_relevant)

        if args.estimators:
            LOGGER.info("Pickling %s", args.estimators.name)
            with gzip.open(args.estimators.open("wb"), "wb") as f:
                pickle.dump(estimators, f)
    else:
        LOGGER.info("Unpickling %s", args.estimators.name)
        with gzip.open(args.estimators.open("rb"), "rb") as f:
            estimators = pickle.load(f)
    if args.plots:
        LOGGER.info("Computing density, and probability estimates for a plot")
        samples = linspace(0, 1, SAMPLING_FREQUENCY)
        estimates = get_estimates(estimators, samples, args.num_workers)
        figure = plot_estimates(samples, estimates)
        for plot_path in args.plots:
            LOGGER.info("Plotting %s", plot_path.name)
            figure.savefig(plot_path)


if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()

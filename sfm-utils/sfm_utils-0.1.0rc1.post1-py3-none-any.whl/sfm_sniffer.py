#!/usr/bin/env python3
"""SFM File Sniffer

Usage:
  sfm_sniffer.py [--tags=<dictionary>] [--summary] [--normal|--stricter|--strictest] <file>
  sfm_sniffer.py --dumptags
  sfm_sniffer.py (-h | --help)
  sfm_sniffer.py --version

Options:
  -t --tags=file  Read a dictionary file that maps tags to labels.
                  If unspecified, the default MDF tag labels will be used.
  -s --summary    Output a summary report only.
  -1 --normal     Apply normal type deduction rules.
  -2 --stricter   Apply stricter type deduction rules.
  -3 --strictest  Apply strictest type deduction rules.
  -d --dumptags   Print the default SFM tag dictionary in the format
                  used by --tags
  -h --help       Show this screen.
  --version       Show version.

Applying stricter type deduction rules will generate a report that
prefers more specific types (such as 'number' or 'word') over more
general types (such as 'optional text'). However, stricter type
deduction rules are more likely to generate a large number of exceptions.

"""
import os
import csv
from .tag_analyser import TagAnalyser

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'VERSION')) as version_file:
    __version__ = version_file.read().strip()

__author__  = "Gavin Falconer (gfalconer@expressivelogic.com)"

# The set of known tags.
# As documented in:
# Making Dictionaries - A guide to lexicography and the
# Multi-Dictionary Formatter : Software version 1.0
# David F. Coward, Charles E. Grimes
# (C) SIL International 2000
# ISBN 1-55671-011-9
__default_tag_dictionary = {
    r"\lx": "lexeme",
    r"\hm": "homonym",
    r"\lc": "lexical citation",
    r"\ph": "phonetic form",
    r"\se": "subentry",
    r"\ps": "part of speech",
    r"\pn": "part of speech (national)",
    r"\sn": "sense number",
    r"\gv": "gloss (vernacular)",
    r"\dv": "definition (vernacular)",
    r"\ge": "gloss (english)",
    r"\re": "reversal (english)",
    r"\we": "word-level gloss (english)",
    r"\de": "definition (english)",
    r"\gn": "gloss (national)",
    r"\rn": "reversal (national)",
    r"\wn": "word-level gloss (national)",
    r"\dn": "definition (national)",
    r"\gr": "gloss (regional)",
    r"\rr": "reversal (regional)",
    r"\wr": "word-level gloss (regional)",
    r"\dr": "definition (regional)",
    r"\lt": "literally",
    r"\sc": "scientific name",
    r"\rf": "reference",
    r"\xv": "example (vernacular)",
    r"\xe": "example (english)",
    r"\xn": "example (national)",
    r"\xr": "example (regional)",
    r"\xg": "example (gloss for interlinearizing)",
    r"\ue": "usage (english)",
    r"\un": "usage (national)",
    r"\ur": "usage (regional)",
    r"\uv": "usage (vernacular)",
    r"\ee": "encyclopaedic information (english)",
    r"\en": "encyclopaedic information (national)",
    r"\er": "encyclopaedic information (regional)",
    r"\ev": "encyclopaedic information (vernacular)",
    r"\oe": "only (restrictions - english)",
    r"\on": "only (restrictions - national)",
    r"\or": "only (restrictions - regional)",
    r"\ov": "only (restrictions - vernacular)",
    # todo:
    # r"\lf",
    # r"\le",
    # r"\ln",
    # r"\lr"
    r"\sy": "synonyms",
    r"\an": "antonyms",
    r"\mr": "morphology",
    r"\cf": "cross-reference",
    r"\ce": "cross-reference (english gloss)",
    r"\cn": "cross-reference (national gloss)",
    r"\cr": "cross-reference (regional gloss)",
    r"\mn": "main entry cross-reference",
    r"\va": "variant forms",
    r"\ve": "variant (english comment)",
    r"\vn": "variant (national comment)",
    r"\vr": "variant (regional comment)",
    r"\bw": "borrowed word (loan)",
    r"\et": "etymology (historical)",
    r"\eg": "etymology gloss (english)",
    r"\es": "etymology source",
    r"\ec": "etymology comment",
    r"\pd": "paradigm",
    r"\tb": "table",
    r"\sd": "semantic domain",
    r"\is": "index of semantics",
    r"\th": "thesaurus (vernacular)",
    r"\bb": "bibliographical reference",
    r"\pc": "picture",
    r"\nt": "notes",
    r"\so": "source of data",
    r"\st": "status for editing or printing",
    r"\dt": "date of last edit",
}


def report_summary(tags):
    """Print a summary report.

    The summary report lists the number of occurrences of each tag
    and the number of value exceptions for each tag, without giving
    details of exceptions.

    Args:
        tags: tag_analyser.TagCollection
            A dictionary-like collection of tags and associated info

    """
    sorted_tags = sorted(tags,
                         key=lambda entry: entry[1]['count'],
                         reverse=True)
    for tag, info in sorted_tags:
        deduced_type = None
        exceptions = 0
        values = info['values']
        if values:
            deduced_type = values.deduced_type
            exceptions = len(values.type_violations)

        print("{tag:4}: {label:20} : occurrences={count:4} : "
              "type={typename:15} : exceptions={ex_count}".format(
                tag=tag,
                label=info['label'],
                count=info['count'],
                typename=deduced_type if deduced_type else "Unknown",
                ex_count=exceptions))


def report(tags):
    """Print a detailed report.

    The detailed report lists the number of occurrences of each tag
    and the number of value exceptions for each tag.
    For tags that have been annotated with example values, lists
    the examples.
    For tags that have associated value exceptions, lists the location
    and the exception value.

    Args:
        tags: tag_analyser.TagCollection
            A dictionary-like collection of tags and associated info

    Side-effects:
        Adds an 'exception_count' field to the information associated
        with each tag.

    """
    # add an exception count to each tag
    for tag, info in tags:
        values = info['values']
        info['exception_count'] = (
            len(values.type_violations) if values else 0
        )

    # tag formatting function
    def print_tag(tag, info):
        deduced_type = None
        examples = None
        exceptions = []
        values = info['values']
        if values:
            deduced_type = values.deduced_type
            exceptions = values.type_violations
            examples = values.examples
        print("{tag:4}: {label:20}: occurrences={count:4}: "
              "type={typename}".format(
                tag=tag,
                label=info['label'],
                count=info['count'],
                typename=deduced_type if deduced_type else "Unknown"))
        if examples:
            print("Example values:")
            print(str(examples))
        if exceptions:
            print("{count} exception{s} "
                  "for {tag} of type '{typename}':".format(
                    tag=tag,
                    count=info['exception_count'],
                    typename=deduced_type,
                    s="s" if info['exception_count'] > 1 else ""))
            for e in exceptions:
                value = e['value'] if e['value'] is not None else "<no value>"
                context = e['context']
                line = context['line_number'] if context else "???"
                print("line {line:4}: {tag} {value}".format(
                        line=line,
                        tag=tag,
                        value=value))

    # sort by descending occurrence
    sorted_tags = sorted(tags, key=lambda t: t[1]['count'], reverse=True)

    # list tags having no exceptions
    no_error_tags = filter(
        lambda t: t[1]['exception_count'] == 0,
        sorted_tags)
    for tag, info in no_error_tags:
        print_tag(tag, info)

    # sort by descending number of exceptions
    sorted_tags = sorted(tags, key=lambda t: t[1]['exception_count'], reverse=True)

    # list tags with exceptions
    error_tags = filter(
        lambda t: t[1]['exception_count'] > 0,
        sorted_tags)
    for tag, info in error_tags:
        print("====================================")
        print_tag(tag, info)


def dump_dict(tag_dictionary):
    """Dump the given tag label dictionary to stdout as CSV."""
    writer = csv.writer(sys.stdout)
    writer.writerows(tag_dictionary.items())


def read_dict(filename):
    """Read a tag label CSV file and return the tag label dictionary"""
    tag_dictionary = dict()
    with (open(filename, encoding='utf8', newline='')) as f:
        reader = csv.reader(f)
        for row in reader:
            tag = row[0]
            definition = row[1]
            tag_dictionary[tag] = definition
    return tag_dictionary


def analyse(filename, tag_dictionary, strictness=1.0, summarize=False):
    """Analyse an SFM file and print the results of the analysis."""
    analyser = TagAnalyser(tag_dictionary, strictness)
    results = analyser.analyse(filename)
    if summarize:
        report_summary(results)
    else:
        report(results)


def main():
    from docopt import docopt

    # parse the command line arguments
    arguments = docopt(__doc__, version=__version__)
    # print(arguments)

    # get the dictionary for tag labels
    tag_dictionary = __default_tag_dictionary
    if arguments["--tags"] is not None:
        tag_dictionary = read_dict(arguments["--tags"])

    # interpret arguments
    strictness = 1.0
    if arguments["--stricter"]:
        strictness = 1.5
    if arguments["--strictest"]:
        strictness = 3.5

    filename = arguments["<file>"]
    summarize = arguments["--summary"]

    # execute a command
    if arguments["--dumptags"]:
        dump_dict(tag_dictionary)
    else:
        analyse(filename, tag_dictionary, strictness, summarize)

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())

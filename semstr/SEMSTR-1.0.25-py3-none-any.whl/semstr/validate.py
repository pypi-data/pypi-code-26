import argparse
import sys
from itertools import groupby, islice

from ucca import layer0, layer1, validation
from ucca.normalization import normalize

from semstr.constraint.amr import AmrConstraints
from semstr.constraint.conllu import ConlluConstraints
from semstr.constraint.sdp import SdpConstraints
from semstr.constraints import UccaConstraints, Direction
from semstr.convert import iter_passages

CONSTRAINTS = {
    None:     UccaConstraints,
    "amr":    AmrConstraints,
    "sdp":    SdpConstraints,
    "conllu": ConlluConstraints,
}


def detect_cycles(passage):
    stack = [list(passage.layer(layer1.LAYER_ID).heads)]
    visited = set()
    path = []
    path_set = set(path)
    while stack:
        for node in stack[-1]:
            if node in path_set:
                yield "Detected cycle (%s)" % "->".join(n.ID for n in path)
            elif node not in visited:
                visited.add(node)
                path.append(node)
                path_set.add(node)
                stack.append(node.children)
                break
        else:
            if path:
                path_set.remove(path.pop())
            stack.pop()


def join(edges):
    return ", ".join("%s-[%s%s]->%s" % (e.parent.ID, e.tag, "*" if e.attrib.get("remote") else "", e.child.ID)
                     for e in edges)


def validate(passage, args):
    if args.normalize:
        normalize(passage, extra=args.extra_normalization)
    if args.ucca_validation:
        validation.validate(passage)
    else:  # Generic validations depending on format-specific constraints
        constraints = CONSTRAINTS[passage.extra.get("format", args.format)](args)
        yield from detect_cycles(passage)
        l0 = passage.layer(layer0.LAYER_ID)
        l1 = passage.layer(layer1.LAYER_ID)
        for terminal in l0.all:
            yield from check_orphan_terminals(constraints, terminal)
            yield from check_root_terminal_children(constraints, l1, terminal)
            yield from check_multiple_incoming(constraints, terminal)
        yield from check_top_level_allowed(constraints, l1)
        for node in l1.all:
            yield from check_multigraph(constraints, node)
            yield from check_implicit_children(constraints, node)
            yield from check_multiple_incoming(constraints, node)
            yield from check_top_level_only(constraints, l1, node)
            yield from check_required_outgoing(constraints, node)
            yield from check_tag_rules(constraints, node)


def check_orphan_terminals(constraints, terminal):
    if not constraints.allow_orphan_terminals:
        if not terminal.incoming:
            yield "Orphan %s terminal (%s) '%s'" % (terminal.tag, terminal.ID, terminal)


def check_root_terminal_children(constraints, l1, terminal):
    if not constraints.allow_root_terminal_children:
        if set(l1.heads).intersection(terminal.parents):
            yield "Terminal child of root (%s) '%s'" % (terminal.ID, terminal)


def check_top_level_allowed(constraints, l1):
    if constraints.top_level_allowed:
        for head in l1.heads:
            for edge in head:
                if edge.tag not in constraints.top_level_allowed:
                    yield "Top level %s edge (%s)" % (edge.tag, edge)


def check_multigraph(constraints, node):
    if not constraints.multigraph:
        for parent_id, edges in groupby(node.incoming, key=lambda e: e.parent.ID):
            edges = list(edges)
            if len(edges) > 1:
                yield "Multiple edges from %s to %s (%s)" % (parent_id, node.ID, join(edges))


def check_implicit_children(constraints, node):
    if constraints.require_implicit_childless and node.attrib.get("implicit") and len(node.outgoing) > 1:
        yield "Implicit node with children (%s)" % node.ID


def check_multiple_incoming(constraints, node):
    if constraints.possible_multiple_incoming:
        incoming = [e for e in node.incoming if not e.attrib.get("remote") and
                    e.tag not in constraints.possible_multiple_incoming]
        if len(incoming) > 1:
            yield "Multiple incoming non-remote (%s)" % join(incoming)


def check_top_level_only(constraints, l1, node):
    if constraints.top_level_only and node not in l1.heads:
        for edge in node:
            if edge.tag in constraints.top_level_only:
                yield "Non-top level %s edge (%s)" % (edge.tag, edge)


def check_required_outgoing(constraints, node):
    if constraints.required_outgoing and all(n.tag == layer1.NodeTags.Foundational for n in node.children) and \
            not any(e.tag in constraints.required_outgoing for e in node):
        yield "Non-terminal without outgoing %s (%s)" % (constraints.required_outgoing, node.ID)


def check_tag_rules(constraints, node):
    for rule in constraints.tag_rules:
        for edge in node:
            for violation in (rule.violation(node, edge, Direction.outgoing, message=True),
                              rule.violation(edge.child, edge, Direction.incoming, message=True)):
                if violation:
                    yield "%s (%s)" % (violation, join([edge]))
            if not constraints.allow_edge(edge):
                "Illegal edge: %s" % join([edge])
            if not constraints.allow_parent(node, edge.tag):
                yield "%s may not be a '%s' parent (%s, %s)" % (node.ID, edge.tag, join(node.incoming), join(node))
            if not constraints.allow_child(edge.child, edge.tag):
                yield "%s may not be a '%s' child (%s, %s)" % (
                    edge.child.ID, edge.tag, join(edge.child.incoming), join(edge.child))


def main(args):
    errors = ((p.ID, list(validate(p, args=args)))
              for p in iter_passages(args.filenames, desc="Validating", split=args.split))
    errors = dict(islice(((k, v) for k, v in errors if v), 1 if args.strict else None))
    if errors:
        id_len = max(map(len, errors))
        for passage_id, es in sorted(errors.items()):
            for i, e in enumerate(es):
                print("%-*s|%s" % (id_len, "" if i else passage_id, e))
        sys.exit(1)
    else:
        print("No errors found.")


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Validate UCCA passages")
    argparser.add_argument("filenames", nargs="+", help="files or directories to validate")
    argparser.add_argument("-f", "--format", help="default format (if cannot determine by suffix)")
    argparser.add_argument("-s", "--split", action="store_true", help="split each sentence to its own passage")
    argparser.add_argument("-i", "--implicit", action="store_true", help="allow implicit nodes")
    argparser.add_argument("-S", "--strict", action="store_true", help="fail as soon as a violation is found")
    argparser.add_argument("-u", "--ucca-validation", action="store_true", help="apply UCCA-specific validations")
    argparser.add_argument("-n", "--normalize", action="store_true", help="more normalization rules")
    argparser.add_argument("-e", "--extra-normalization", action="store_true", help="more normalization rules")
    main(argparser.parse_args())

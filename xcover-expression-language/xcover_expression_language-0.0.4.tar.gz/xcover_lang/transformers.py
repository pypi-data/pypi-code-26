import operator
from functools import reduce
from lark import (
    Transformer,
    Tree,
)
from lark.tree import Discard


def recrusive_get_num(tree):
    if not isinstance(tree, Tree):
        return tree
    val = recrusive_get_num(tree.children[0])
    if val:
        if str(val).isdigit():
            return float(val)
        else:
            return val
    else:
        return val


class TreeTransformer(Transformer):
    number = float

    def __init__(self, vars):
        self.vars = vars or {}

    def term_add(self, terms):
        return reduce(operator.__add__, (map(recrusive_get_num, terms)))

    def term_subtract(self, terms):
        return reduce(operator.__sub__, map(recrusive_get_num, terms))

    def term_mul(self, terms):
        return reduce(operator.mul, map(recrusive_get_num, terms), 1)

    def term_div(self, terms):
        return reduce(operator.truediv, map(recrusive_get_num, terms))

    def neg(self, term):
        return -recrusive_get_num(term[0])

    def string(self, s):
        return s[0][1:-1]

    def number(self, n):
        return float(n[0].value)

    def func_call(self, terms):
        func_name = terms[0].value
        args = list(map(recrusive_get_num, terms[1].children))
        if func_name == 'max':
            return max(args)
        elif func_name == 'min':
            return min(args)
        elif func_name == 'if_cond':
            return args[1] if args[0] else args[2]
        else:
            raise Exception('Unkown function {0}'.format(func_name))

    def eval_equalities_test(self, terms):
        left = recrusive_get_num(terms[0])
        right = recrusive_get_num(terms[2])

        op = terms[1].value

        ops_lookup = {
            '<': lambda a, b: a < b,
            '>': lambda a, b: a > b,
            '==': lambda a, b: a == b,
            '>=': lambda a, b: a >= b,
            '<=': lambda a, b: a <= b,
            '<>': lambda a, b: a != b,
        }
        comparator = ops_lookup.get(op, None)
        if not comparator:
            raise Exception('Unknown operator, supports only < > == >= <= <>')

        return comparator(left, right)

    def assign_var(self, _vars):
        if isinstance(_vars[1], Tree):
            items = []
            for c in _vars[1].children:
                try:
                    items.append(self.transform(c) if isinstance(c, Tree) else c)
                except Discard:
                    pass

            self.vars[_vars[0].value] = items[0]
            return items[0]
        else:
            self.vars[_vars[0].value] = _vars[1]
            return _vars[1]

    def bool_eval(self, terms):
        return terms[0] or terms[1]

    def access_object(self, _vars):
        return self.vars.get(_vars[0], {}).get(str(_vars[1]))

    def access_var(self, name):
        return self.vars[name[0].value]

    def term(self, term):
        return term[0]

    def eval_expression(self, tree):
        return tree[0].children[0]

    def eval_or_expression(self, terms):

        if len(terms) == 1:
            result = True
            for term in terms:
                val = recrusive_get_num(term)
                if not bool(val):
                    result = False
                    break
        else:
            result = None
            for term in terms:
                val = recrusive_get_num(term)
                if bool(val):
                    return val
                else:
                    result = val
        return result

    def eval_and_test(self, terms):
        result = True
        for term in terms:
            val = recrusive_get_num(term)
            if not bool(val):
                result = False
                break
        return result

    def eval_not(self, terms):
        return not recrusive_get_num(terms[0])

    def eval_membership_test(self, terms):
        return terms[0] in terms[1]

    list = list
    pair = tuple
    object = dict

    null = lambda self, _: None
    true = lambda self, _: True
    false = lambda self, _: False

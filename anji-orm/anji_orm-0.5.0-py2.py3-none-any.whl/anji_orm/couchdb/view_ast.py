import abc
from typing import Optional, Dict, List

from ..core import AggregationType, QueryRow, QueryBiStatement, StatementType, Interval

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.5.0"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = ["CouchDBFilter", "CouchDBMap", "CouchDBReduce", "CouchDBFunctionPart"]

SELECTOR_STATEMENT_MAPPING = {
    "$eq": "==",
    "$ne": "!=",
    "$lte": "<=",
    "$gte": ">=",
    "$lt": "<",
    "$gt": ">"
}


def convert_attribute(attribute):
    if isinstance(attribute, QueryRow):
        return f"doc.{attribute.row_name}"
    return attribute


class CouchDBFunctionPart(abc.ABC):

    __slots__: List[str] = []

    @abc.abstractmethod
    def to_javascript(self) -> Optional[str]:
        pass


class CouchDBFilter(CouchDBFunctionPart):

    __slots__ = ['conditions']

    def __init__(self, db_query_selector: Dict) -> None:
        self.conditions: List[str] = []
        self.add_parsed(db_query_selector)

    def add_parsed(self, db_query_selector: Dict) -> None:
        for key, selector_conditinios in db_query_selector.items():
            if key == '_id' and selector_conditinios == {'$gt': None}:
                continue
            for condition_key, condition_value in selector_conditinios.items():
                if condition_key == '$in':
                    self.conditions.append(f"{str(condition_value)}.includes(doc.{condition_value})")
                else:
                    self.conditions.append(
                        f"doc.{key} {SELECTOR_STATEMENT_MAPPING[condition_key]}"
                        f" {condition_value}"
                    )

    def add(self, query: QueryBiStatement) -> None:
        left = convert_attribute(query.left)
        right = convert_attribute(query.right)
        if query.statement_type == StatementType.bound:
            interval: Interval = right
            left_operation = '>=' if interval.left_close else '>'
            right_operation = '<=' if interval.right_close else '<'
            self.conditions.append(f"{left} {left_operation} {interval.left_bound}")
            self.conditions.append(f"{left} {right_operation} {interval.right_bound}")
        elif query.statement_type == StatementType.isin:
            self.conditions.append(f"{right}.includes({left})")
        else:
            self.conditions.append(
                f"{left} {query.statement_type.value} {right}"
            )

    def to_javascript(self) -> Optional[str]:
        if not self.conditions:
            return None
        return ' && '.join(self.conditions)


class CouchDBMap(CouchDBFunctionPart):

    __slots__ = ['filter', 'emit']

    def __init__(self, db_query: Dict, row: Optional[QueryRow] = None) -> None:
        self.filter = CouchDBFilter(db_query['selector'])
        self.emit = ''
        self.set_emit_function(row)

    def set_emit_function(self, row: Optional[QueryRow] = None) -> None:
        if row:
            self.emit = f"emit(doc._id, doc.{row.row_name});"
        else:
            self.emit = f"emit(doc._id, doc);"

    def to_javascript(self) -> str:
        function_lines = ['function (doc){']
        selection_filter = self.filter.to_javascript()
        if selection_filter:
            function_lines.append(f"if ({selection_filter}) {'{'}")
            function_lines.append(self.emit)
            function_lines.append("}")
        else:
            function_lines.append(self.emit)
        function_lines.append('}')
        return '\n'.join(function_lines)


class CouchDBReduce(CouchDBFunctionPart):

    __slots__ = ['type']

    def __init__(self, aggregation_type: AggregationType) -> None:
        self.type = aggregation_type

    def to_javascript(self) -> str:
        if self.type in (AggregationType.sum, AggregationType.count):
            return f"_{self.type.name}"
        if self.type in (AggregationType.min, AggregationType.max):
            comparation_operator = '>' if self.type == AggregationType.max else '<'
            return (
                "function (keys, values) {\n"
                "return values.reduce(function (p, v) {\n"
                f"return (p {comparation_operator} v ? p : v);\n"
                "});"
                '}'
            )
        return (
            "function (keys, values) {\n"
            "return sum(values) / values.lenght"
            '}'
        )

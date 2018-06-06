import json
from typing import List, Union


class WorkflowIcon:
    def __init__(self, path, type=None):  # pylint: disable=W0622
        self.path = path
        self.type = type

    def __str__(self):
        return self.to_json()

    def __repr__(self):
        return "<WorkflowIcon path='{}'>".format(self.path)

    def to_json(self, as_str: bool = True) -> Union[str, dict]:
        tmp = {
            "path": self.path,
        }

        if self.type:
            tmp["type"] = self.type,

        if as_str:
            return json.dumps(tmp)

        return tmp


class WorkflowItem:
    def __init__(
            self, title: str, subtitle: str,
            arg: str, icon: WorkflowIcon = None,
            uid: str = None, valid: bool = True,
            match: str = None, autocomplete: str = None,
            type: str = "default",  # pylint: disable=W0622
            mods: dict = None, text: dict = None,
            quicklookurl: str = None
    ):
        self.uid = uid
        self.title = title
        self.subtitle = subtitle
        self.arg = arg
        self.icon = icon
        self.valid = valid
        self.match = match
        self.autocomplete = autocomplete
        self.type = type
        self.mods = mods
        self.text = text
        self.quicklookurl = quicklookurl

    def __str__(self):
        return self.to_json()

    def __repr__(self):
        return "<WorkflowItem title='{}'>".format(self.title)

    def to_json(self, as_str: bool = True) -> Union[str, dict]:
        tmp = {
            "title": self.title,
            "subtitle": self.subtitle,
            "arg": self.arg,
            "valid": self.valid,
        }

        if self.icon:
            tmp["icon"] = self.icon.to_json(),

        if self.uid:
            tmp["uid"] = self.uid

        if self.match:
            tmp["match"] = self.match

        if self.autocomplete:
            tmp["autocomplete"] = self.autocomplete

        if self.type:
            tmp["type"] = self.type

        if self.mods:
            tmp["mods"] = self.mods

        if self.text:
            tmp["text"] = self.text

        if self.quicklookurl:
            tmp["quicklookurl"] = self.quicklookurl

        if as_str:
            return json.dumps(tmp)

        return tmp


class WorkflowVariable():
    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value

    def __str__(self):
        return self.to_json()

    def __repr__(self):
        return "<WorkflowVariable name={} value={}>".format(
            self.name, self.value
        )

    def to_json(self, as_str: bool = True) -> Union[str, dict]:
        tmp = {
            self.name: self.value
        }

        if as_str:
            return json.dumps(tmp)

        return tmp


class Workflow:
    def __init__(
            self,
            items: List[WorkflowItem] = None,
            variables: List[WorkflowVariable] = None,
            rerun: float = None
    ):
        self.items = items or []
        self.variables = variables or []
        self.rerun = rerun

    def to_json(self, as_str: bool = True) -> Union[str, dict]:
        tmp = {
            "items": [item.to_json(as_str=False) for item in self.items],
            "variables": {var.name: var.value for var in self.variables}
        }

        if self.rerun:
            tmp["rerun"] = self.rerun

        if as_str:
            return json.dumps(tmp)

        return tmp

    def __str__(self):
        return self.to_json()

    def __repr__(self):
        return "<Workflow items=[{}] variables=[{}] rerun = {}>".format(
            len(self.items), len(self.variables), self.rerun
        )

    def add_items(self, *args) -> 'Workflow':
        for arg in args:
            self.add_item(arg)

        return self

    def add_variables(self, *args) -> 'Workflow':
        for arg in args:
            self.add_variable(arg)

        return self

    def add_item(self, item: WorkflowItem) -> 'Workflow':
        """
        Test
        """

        self.items.append(item)
        return self

    def add_variable(self, variable: WorkflowVariable) -> 'Workflow':
        self.variables.append(variable)
        return self

    def add(self, *args) -> 'Workflow':
        for thing in args:
            if isinstance(thing, WorkflowItem):
                self.add_item(thing)
            elif isinstance(thing, WorkflowVariable):
                self.add_variable(thing)
            else:
                raise TypeError("Can only accept WorkflowVariable or WorkflowItem")

        return self

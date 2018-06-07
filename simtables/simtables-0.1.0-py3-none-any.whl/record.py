_NO_DEFAULT = object()
class Record(dict):
    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except TypeError:
            return Record({k: dict.__getitem__(self, k) for k in key})

    def __setitem__(self, key, value):
        try:
            dict.__setitem__(self, key, value)
        except TypeError:
            for k in key:
                dict.__setitem__(self, k, value[k])

    def get(self, key, default=None):
        try:
            return dict.get(self, key, default)
        except TypeError:
            if default is None:
                default = {}
            new_record = Record()
            for k in key:
                if k in self:
                    new_record[k] = self[k]
                elif k in default:
                    new_record[k] = default[k]
            return new_record

    def pop(self, key, default=_NO_DEFAULT):
        try:
            if default is _NO_DEFAULT:
                return dict.pop(self, key)
            else:
                return dict.pop(self, key, default)
        except TypeError:
            backup = Record(self)
            try:
                if default is _NO_DEFAULT:
                    return Record(
                        {k: dict.pop(self, k) for k in key})
                else:
                    new_record = Record()
                    for k in key:
                        if k in self:
                            new_record[k] = dict.pop(self, k)
                        else:
                            new_record[k] = default[k]
                    return new_record
            except:
                for k in backup:
                    self[k] = backup[k]
                raise

    def popitem(self, key, default=_NO_DEFAULT):
        raise NotImplementedError

    def setdefault(self, key, default=_NO_DEFAULT):
        raise NotImplementedError

    def copy(self):
        return Record(dict.copy(self))

    def __setattr__(self, key, value):
        raise RuntimeError

    def __str__(self):
        try:
            _, width = subprocess.check_output(["stty", "size"]).split()
        except:
            width = 40
        width = int(width)

        vertical_edge = "".join(("+", "-"*(width - 2), "+"))

        pairs = [
           (str(key), str(item).replace("\n", " ")[:width - 6 - len(key)])
            for key, item in self.items()
            ]

        return "\n".join(
            [vertical_edge,]
            + [
                "".join(
                    (
                        "| ",
                        key,
                        ": ",
                        item,
                        " "*(width - 6 - len(key) - len(item)),
                        " |",
                    )
                )
               for key, item in pairs
            ]
            + [vertical_edge,]
        )

    def __repr__(self):
        return ''.join(('Record({', ', '.join([': '.join((key, repr(item))) for key, item in self.items()]), '})'))

    @staticmethod
    def _mergable(record1, record2):
        return not any(
            record1[key] != record2[key] for key in record1 if key in record2)

    @staticmethod
    def merge(records):
        new_record = Record()
        for record in records:
            if any(record[key] != new_record[key]
                   for key in record if key in new_record):
                raise ValueError("Records clash on key")
            else:
                new_record.update(record)
        return new_record

    @staticmethod
    def merge_conflicts(records):
        new_record = Record()
        conflicts = []
        for record in records:
            for key in record:
                if key not in new_record:
                    new_record[key] = record[key]
                elif key in new_record and new_record[key] != record[key]:
                    conflicts.append(key)
        return conflicts

    def without(self, keys):
        return self[set(self) - set(keys)]

    def __add__(self, other):
        return Record.merge((self, other))

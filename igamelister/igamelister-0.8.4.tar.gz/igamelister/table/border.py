class Border:
    def __init__(self):
        self.tl: str = "."
        self.tr: str = "."
        self.bl: str = "`"
        self.br: str = "'"

        self.t: str = "-"
        self.l: str = "|"
        self.r: str = "|"
        self.b: str = "-"

        self.mv = "|"
        self.mh = "-"
        self.ms: str = "+"

        self.ts: str = "v"
        self.ls: str = ">"
        self.rs: str = "<"
        self.bs: str = "^"

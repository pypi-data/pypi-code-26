__version__ = '0.1.0'

import numpy as np
from numpngw import write_apng

class Nummu:

    def __init__(self, height, weight):
        self.seq = []
        self.is_quit = False
        self.modules = []
        self.resources = {}
        self.height = height
        self.weight = weight

    def add(self, name, type, **meta):
        self.resources[name] = dict(type=type, **meta)

    def extend(self, mod):
        self.modules.append(mod)

    def quit(self):
        self.is_quit = True

    def _run_init(self):
        for mod in self.modules:
            if hasattr(mod, 'init'):
                mod.init()

    def _run_update(self, delta):
        for mod in self.modules:
            if hasattr(mod, 'update'):
                mod.update(delta)

    def _run_draw(self):
        palette = np.zeros((self.height, self.weight), dtype=np.uint8)
        for mod in self.modules:
            if hasattr(mod, 'draw'):
                mod.draw(palette)
        self.seq.append(palette)

    def export(self, filename, delay, length=30000):
        self._run_init()
        progress = 0
        while not self.is_quit:
            try:
                self._run_update(delay)
                self._run_draw()
                progress += delay
                if progress >= length:
                    raise StopIteration
            except StopIteration:
                self.quit()
        write_apng(filename, self.seq, delay=delay, use_palette=True)

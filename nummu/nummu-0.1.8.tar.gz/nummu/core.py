import warnings

import numpy as np
from array2gif import write_gif
from numpngw import write_apng

class Nummu:

    def __init__(self, height, weight):
        self.seq = []
        self.is_quit = False
        self.modules = []
        self.resources = {}
        self.height = height
        self.weight = weight

    def load(self, name, type, **meta):
        self.resources[name] = dict(type=type, **meta)

    def add(self, mod):
        self.modules.append(mod)

    def quit(self):
        self.is_quit = True

    def _run_init(self):
        for mod in self.modules:
            if hasattr(mod, 'init'):
                warnings.warn('init is deprecated, use __init__ instead.', DeprecationWarning)
                mod.init()

    def _run_update(self, delta):
        for mod in self.modules:
            if hasattr(mod, 'update'):
                mod.update(delta)

    def _run_draw(self):
        palette = np.zeros((self.height, self.weight, 3), dtype=np.uint8)
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
        if filename.endswith('.png'):
            write_apng(filename, self.seq, delay=delay, use_palette=True)
        elif filename.endswith('.gif'):
            # array2gif requires a transposed matrix compared to numpngw.
            seq = []
            for s in self.seq:
                seq.append(np.transpose(s, axes=[1, 0, 2]))
            write_gif(seq, filename, fps=int(1000/delay))
        else:
            raise NotImplementedError('Unsupported file format')

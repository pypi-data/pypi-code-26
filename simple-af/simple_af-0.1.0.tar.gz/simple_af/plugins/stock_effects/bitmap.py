import random
import numpy as np
from collections import namedtuple
from simple_af.model import Effect, Scene, MultiEffect
from simple_af.state import STATE

#Name is just for easier print/debugging
Bitmap = namedtuple("Bitmap", ["name", "height", "width", "bitmap"])

BIG_LETTERS = {
    # 8x4
    'B': Bitmap("BigB", 8, 4, [ [0,0],[1,0],[2,0],  [0,1],[3,1],  [0,2],[3,2],  [0,3],[1,3],[2,3],  [0,4],[1,4],[2,4],  [0,5],[3,5],  [0,6],[3,6],  [0,7],[1,7],[2,7] ])
}

SMALL_LETTERS = {
    #3x3
    'H': Bitmap("SmallH", 3,3, [ [0,0],[2,0],  [0,1],[1,1],[2,1],  [0,2],[2,2] ]),
    'O': Bitmap("SmallO", 3, 3, [ [0,0],[1,0],[2,0],  [0,1], [2,1],  [0,2], [1,2], [2,2] ]),
    'T': Bitmap("SmallT", 3, 3, [ [0,0],[1,0],[2,0],  [1,1],  [1,2] ])
}

#5x5
LETTERS = {
    'C': Bitmap("C", 5, 5, [ [1,0],[2,0],[3,0],[4,0],  [0,1],  [0,2],  [0,3],  [1,4],[2,4],[3,4],[4,4] ]),  #Really long. Maybe add another left vertical column
    'M': Bitmap("M", 5, 5, [ [0,0],[4,0],  [0,1],[1,1],[3,1],[4,1],  [0,2],[2,2],[4,2],  [0,3],[4,3],  [0,4],[4,4] ]),
    'N': Bitmap("N", 5, 5, [ [0,0],[4,0],  [0,1],[1,1],[4,1],  [0,2],[2,2],[4,2],  [0,3],[3,3],[4,3],  [0,4],[4,4] ]),
    'O': Bitmap("O", 5, 5, [ [1,0],[2,0],[3,0],  [0,1],[4,1],  [0,2],[4,2],  [0,3],[4,3],  [1,4],[2,4],[3,4] ]),
    'T': Bitmap("T", 5, 5, [ [0,0],[1,0],[2,0],[3,0],[4,0],  [2,1],  [2,2], [2,3], [2,4] ]),
    'Y': Bitmap("Y", 5, 5, [ [0,0],[4,0],  [1,1],[3,1],  [2,2],  [2,3],  [2,4] ])
}

def createPoints(rows, cols):
    return [[c,r] for r in rows for c in cols]

#6X6
LETTERS_SIX = {
    ' ': Bitmap(" ", 0, 1, []),
    #Kind of ugly
    'A': Bitmap('A', 6, 6, [ [2,0],[3,0],  [1,1],[4,1],  [1,2],[4,2]] + createPoints([3],range(1,5)) + createPoints([4,5],[0,5])),
    'D': Bitmap("D", 6, 5, createPoints(range(6), [0,1]) + createPoints([0,5],[2]) + [ [3,1], [4,2], [4,3], [3,4] ]),
    'E': Bitmap('E', 6, 6, createPoints([0,5], range(6)) + createPoints([2,3], range(5)) + createPoints([1,4], [0,1])  ),
    'H': Bitmap('H', 6, 6, createPoints(range(6), [0,1,4,5]) + createPoints([2,3],[2,3])),
    'M': Bitmap("M", 6, 6, [[c,r] for r in range(6) for c in [0,5]] + [[1,1],[2,2],[3,2],[4,1]]),
    'N': Bitmap("N", 6, 6, [[c,r] for r in range(6) for c in [0,5]] + [[c,c] for c in range(1,5)]),
    'O': Bitmap("O", 6, 6, [[c,r] for r in [0,5] for c in range(1,5)] + [[c,r] for r in range(1,5) for c in [0,1,4,5]] + [[c,r] for r in [1,4] for c in range(2,4)]),
    'R': Bitmap('R', 6, 6, createPoints(range(6),[0,1]) + [[5,1],[5,2]] + createPoints([0,3], range(2,5)) + [[5,4],[5,5]]  ),
    'T': Bitmap("T", 6, 6, [[c,r] for r in [0,1] for c in range(6)] + [[c,r] for r in range(2,6) for c in [2,3]]),
    'U': Bitmap("U", 6, 6, createPoints(range(5), [0,1,4,5]) + createPoints([5], range(1,5)) + [[2,4],[3,4]] ),
    'Y': Bitmap("Y", 6, 6, [[c,c] for c in [0,1]] + [[c,5-c] for c in [4,5]] + [[c,r] for c in [2,3] for r in range(2,6)])
}

#A slow function to concat two bitmaps. Results in lots of overhead
def concat_bitmaps(a,b,space=0):
    return Bitmap(a.name+b.name, a.height+b.height, a.width+b.width+space, a.bitmap+map(lambda point: [point[0]+a.width+space, point[1]], b.bitmap))

def createWord(bitmaps, word, space=1):
    return reduce(lambda a,b: concat_bitmaps(a,b,space), [bitmaps[letter] for letter in word])

CACHED_WORDS = {
    'TONY': createWord(LETTERS_SIX, "TONY", 1),
    'TONYx3': createWord(LETTERS_SIX, "TONY  TONY  TONY", 1),

    'DRUM HARDER': createWord(LETTERS_SIX, "DRUM HARDER")
}

class StaticBitmap(Effect):
    def __init__(self, bitmap, color, direction, top_row, left_col=None):
        Effect.__init__(self)
        self.color = color
        self.bitmap = bitmap
        #Default to centered
        left_col = left_col if left_col != None else computeCenteredLeft(bitmap)
        left_offset = left_col if direction>0 else STATE.layout.rows-left_col
        self.pointcloud = map(lambda point: [point[0]*direction+left_offset, point[1]+top_row], bitmap.bitmap)

    def next_frame(self, pixels, t):
        for point in self.pointcloud:
            pixels[point[0],point[1]] = self.color

class FlashBitmap(Effect):
    def __init__(self, bitmap, color, direction, duration, top_row, left_col=None):
        Effect.__init__(self)
        self.color = color
        self.timer = duration
        self.bitmap = bitmap
        #Default to centered
        left_col = left_col if left_col != None else computeCenteredLeft(bitmap)
        left_offset = left_col if direction>0 else STATE.layout.rows-left_col
        self.pointcloud = map(lambda point: [point[0]*direction+left_offset, point[1]+top_row], bitmap.bitmap)

    def next_frame(self, pixels, t):
        for point in self.pointcloud:
            pixels[point[0],point[1]] = self.color
        self.timer = self.timer-1

    def is_completed(self, t):
        return self.timer < 0

class DrawMovingBitmap(Effect):
    def __init__(self, bitmap, color, direction=-1, top_row=0):
        Effect.__init__(self)
        self.color = color
        #TODO: buffer zone
        self.bitmap = bitmap
        self.pointcloud = map(lambda point: [point[0]*direction,point[1]+top_row], bitmap.bitmap)
        self.direction = direction
        self.col = 0 if direction > 0 else STATE.layout.rows-1
        #print self.bitmap, self.pointcloud

    def next_frame(self, pixels, t):
        #TODO faster (numpy manipulations?)
        for point in self.pointcloud:
            if(self.col+point[0]>=0):
                pixels[self.col+point[0],point[1]]=self.color
        self.col += self.direction

    def is_completed(self, t):
        # TODO - edge cases, padding
        return self.col < 0 or self.col >= STATE.layout.rows

def computeCenteredLeft(bitmap):
    return STATE.layout.rows/2-bitmap.width/2



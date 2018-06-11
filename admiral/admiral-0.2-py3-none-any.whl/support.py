import math
import os

class abstractstatic(staticmethod):
    __slots__ = ()
    def __init__(self, function):
        super(abstractstatic, self).__init__(function)
        function.__isabstractmethod__ = True
    __isabstractmethod__ = True

    
class JobmanagerException(Exception):
    pass

class JobSubmissionException(JobmanagerException):
    pass


def path_with_default(path, default=None):
    if path is None:
        if default is None:
            default = os.getcwd()
        path = default
    return path


# def get_chunks(seq, chunk_size):
#     return (seq[pos:pos + chunk_size] for pos in range(0, len(seq), chunk_size))

# def get_nchunks(seq, nchunks):
#     chunk_size = int(math.ceil(len(seq)/nchunks))
#     yield from get_chunks(seq, chunk_size)

def get_nchunks(seq, nchunks):
    """
    Places items from seq into n chunks, moving through first forwards, then backwards
    in order to approximately equalize the weightings (I'm sure there's a better way to do this)

    Ideally, there'd be a system to specify weights so that we can add a bunch of low-weight
    items to the same chunk
    """
    chunks = [list() for i in range(nchunks)]
    incr = +1
    index = 0
    for value in seq:
        chunks[index].append(value)
        index += incr
        if index >= nchunks-1:
            if incr > 0:
                incr = 0
            else:
                incr = -1
        elif index == 0:
            if incr == 0:
                incr = +1
            else:
                incr = 0

    return chunks
import multiprocessing
import math


__all__ = ['multi_process']


def _partition_data(data, num):
    """ Partitions data into pieces.

    :param data: iterable rows
    :param num:  number of pieces
    :return: list of data pieces
    """

    rows = [row for row in data]
    partition_size = math.ceil(len(rows) / num)
    partition = []
    for i in range(num-1):
        partition.append(rows[i*partition_size: (i+1)*partition_size])
    partition.append(rows[(num-1)*partition_size:])

    return partition


def multi_process(func, args, processes=1):

    pool = multiprocessing.Pool(processes=processes)
    rows = [row for row in args[0]]
    partitions = _partition_data(rows, processes)

    result = []
    for part in partitions:
        new_args = tuple([part] + list(args)[1:])
        result.append(pool.apply_async(func, new_args))

    pool.close()
    pool.join()

    for res in result:
        for item in res.get():
            yield item
"""Multiprocessing functions."""
from functools import wraps


def mproc_func(func):
    """Decorate functions to collect results into mproc_results_queue.

    Args:
        mproc_results_queue (mp.Manager.Queue): Queue to put results into.
        mproc_call_index (int): Index of the function call in the mproc_async.
    """
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        mproc_results_queue = kwargs.pop('mproc_results_queue')
        mproc_call_index = kwargs.pop('mproc_call_index')
        # Pass args and kwargs as is to the function.
        try:
            result = func(*args, **kwargs)
        except Exception as ex:
            print("EXCEPTION: {}".format(args))
            print(ex.args)
            result = None
        # Put result into result_queue.
        mproc_results_queue.put((mproc_call_index, result))

    return func_wrapper


def mproc_async(async_func, iterof_iterof_args=None, n_processes=1, queue_size=1):
    """Yield results of a async_function called multiple times using mproc.

    Args:
        async_func (func): A function that is called multiple times using mproc.
            The function MUST CONTAIN AN ARGUMENT called `result_queue`.
            OR
            A function that returns results and has a `mproc_func` DECORATOR.
        iterof_iterof_args (iter of iter): The iterable of arguments that must be passed
            to the `async_func`. The size of the iterable defines the number of mproc
            async function calls.

            Case 1: iterof_iterof_args: [[1], [2], [3]], then calls are f(1), f(2), f(3).

            Case 2: iterof_iterof_args: [[1,2,3], [4,5,6]], then calls are f(1,2,3), f(4,5,6).

            Case 3: iterof_iterof_args: [[], [], []], then calls are f(), f(), f().

        n_processes (int): Number of processes in pool.
        queue_size (int): The size of the internal queue that is used to collect
            results. This helps control memory usage.

    Returns:
        generator: A generator of (call_index, result) of async_func calls.
    """
    # Allocate Multiprocessing Resources
    import multiprocessing as mp
    pool = mp.Pool(n_processes)
    manager = mp.Manager()
    results_queue = manager.Queue(queue_size)
    print("MPROC          : Allocated resources")

    # Produce Async Task Processes
    func_calls = 0
    for call_index, args in enumerate(iterof_iterof_args):
        pool.apply_async(async_func, args=(*args,), kwds={'mproc_results_queue': results_queue,
                                                          'mproc_call_index': call_index})
        func_calls += 1
    else:
        print("MPROC          : Applied {} async calls".format(func_calls))

    # Consume results from queue
    item_count = 0
    while True:
        yield results_queue.get(block=True)
        results_queue.task_done()
        item_count += 1

        if item_count == func_calls:
            print("MPROC          : Joining queue, all calls completed.")
            results_queue.join()
            # Break generator loop
            break

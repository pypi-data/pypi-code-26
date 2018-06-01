from typing import Dict, Iterator, Iterable
import concurrent.futures

import cosmic_ray.execution.execution_engine
import cosmic_ray.work_item
import cosmic_ray.worker


def worker(work_item: Dict, timeout: float, config) -> Dict:
    return dict(
        **cosmic_ray.worker.worker_process(
            work_item,
            timeout,
            config
        )
    )


class LocalPoolExecutionEngine(cosmic_ray.execution.execution_engine.ExecutionEngine):
    "Execution engine that runs jobs on the local machine."

    def __call__(
        self,
        timeout: float,
        pending_work_items: Iterable[cosmic_ray.work_item.WorkItem],
        config
    ) -> Iterator[cosmic_ray.work_item.WorkItem]:
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = {
                executor.submit(
                    worker,
                    dict(**work_item),
                    timeout,
                    config
                )
                for work_item in pending_work_items
            }

            for future in concurrent.futures.as_completed(futures):
                yield cosmic_ray.work_item.WorkItem(future.result())

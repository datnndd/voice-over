from concurrent.futures import ThreadPoolExecutor

from app_core.configure.config import logger

_EXECUTOR = ThreadPoolExecutor(max_workers=4, thread_name_prefix="web-core-reference")


def run_in_threadpool(func, *args, **kwargs):
    def _run():
        try:
            func(*args, **kwargs)
        except Exception as exc:
            logger.exception(f"headless threadpool task failed: {exc}", exc_info=True)

    return _EXECUTOR.submit(_run)

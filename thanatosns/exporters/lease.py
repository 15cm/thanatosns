from decorator import contextmanager
from ninja.schema import Schema
from django.core.cache import cache
from threading import Timer
from django.core.cache import cache
import time


LEASE_RENEW_INTERVAL_SECONDS = 10


# https://stackoverflow.com/a/48741004
class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


def _renew(
    lease_name: str,
    extend_seconds=2 * LEASE_RENEW_INTERVAL_SECONDS,
    at_seconds=time.time(),
):
    cache.set(lease_name, at_seconds + extend_seconds)


def stop(lease_name: str):
    cache.set(lease_name, 0)


def acquire(lease_name: str) -> bool:
    now = time.time()
    lease_expiration = cache.get(lease_name, 0)
    if now < lease_expiration:
        return False
    else:
        _renew(lease_name, extend_seconds=LEASE_RENEW_INTERVAL_SECONDS, at_seconds=now)
        return True


@contextmanager
def refresh_lease_until_done(lease_name: str):
    timer = RepeatTimer(LEASE_RENEW_INTERVAL_SECONDS, _renew, args=(lease_name,))
    timer.start()
    yield
    timer.cancel()
    timer.join()

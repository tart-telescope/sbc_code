import logging
import os
from datetime import datetime, timezone
from time import gmtime, sleep, strftime, time_ns
from typing import Set

import numpy as np

from .tartspi import TartSPI


def load_permute(noisy=False):
    """Load a permutation vector from the file at the given filepath."""
    filepath = os.environ.get("PERMUTE_PATH", "/permute/permute.txt")
    pp = np.loadtxt(filepath, dtype="int")
    return pp


def create_spi_object(runtime_config, speed=16000000):
    perm = load_permute()
    logging.info(f"create_spi_object(speed={speed}")
    try:
        return TartSPI(runtime_config, perm, speed)
    except Exception as e:
        logging.exception(e)
        logging.warn("USING DUMMY SPI MODULE.")
    from .tart_fake_spi import TartFakeSPI

    return TartFakeSPI(runtime_config, perm, speed)


def wait_for_second(second_matches: Set[int], verbose: bool = False) -> datetime:
    """
    Waits until the next second-of-the-minute that is in the allowed set.

    When acquisition is ready, this function blocks until the wall-clock
    second rolls over to one of the values in ``second_matches``.  This
    lets every acquisition start on a deterministic, repeatable grid of
    seconds within each minute.

    Args:
        second_matches: Allowed second-of-the-minute values (0-59) at
            which an acquisition may begin.
            Example: {0, 10, 20, 30, 40, 50} means the acquisition can
            start at any of those seconds — whichever comes next.
        verbose: Print waiting messages if True.

    Returns:
        Timezone-aware datetime in UTC at the moment the target second
        boundary was crossed.
    """
    while True:
        # Get current time in nanoseconds
        now_ns = time_ns()
        now = now_ns / 1_000_000_000.0

        # Get the current second value
        time_struct = gmtime(now)
        current_second = time_struct.tm_sec

        # Check if we're already at a target second
        if current_second in second_matches:
            # We're in a target second, wait until the NEXT target second
            # to avoid immediately returning
            fractional_seconds = now % 1

            # Sleep until 5ms before the next second boundary
            sleep_time = 1 - fractional_seconds - 0.005

            if sleep_time > 0:
                sleep(sleep_time)

            # Busy-wait for the exact second boundary using nanoseconds
            last_second_ns = time_ns()
            last_second = last_second_ns // 1_000_000_000
            while True:
                current_time_ns = time_ns()
                current_second_int = current_time_ns // 1_000_000_000
                if current_second_int > last_second:
                    # We've crossed the boundary, return immediately
                    break

            # Update current_second after crossing boundary
            current_time = current_time_ns / 1_000_000_000.0
            time_struct = gmtime(current_time)
            current_second = time_struct.tm_sec

            # Check if this new second is a target
            if current_second in second_matches:
                return datetime.fromtimestamp(
                    current_time_ns / 1_000_000_000.0, tz=timezone.utc
                )
        else:
            # We're not at a target second, find the next one
            # Calculate how many seconds until the next target
            seconds_until_target = None

            for target in sorted(second_matches):
                if target > current_second:
                    seconds_until_target = target - current_second
                    break

            # If no target found ahead, wrap to the next minute
            if seconds_until_target is None:
                seconds_until_next_minute = 60 - current_second
                next_target = min(second_matches)
                seconds_until_target = seconds_until_next_minute + next_target
            else:
                next_target = current_second + seconds_until_target

            # Print waiting message if verbose
            if verbose:
                print(f"Waiting for Time: :{next_target:02d}")

            # Sleep until close to the target second
            fractional_seconds = now % 1
            total_sleep = seconds_until_target - fractional_seconds - 0.005

            if total_sleep > 0:
                sleep(total_sleep)

            # Busy-wait for the exact second boundary using nanoseconds
            last_second_ns = time_ns()
            last_second = last_second_ns // 1_000_000_000
            while True:
                # busy wait!
                current_time_ns = time_ns()
                current_second_int = current_time_ns // 1_000_000_000
                if current_second_int > last_second:
                    # We've crossed the boundary, return immediately
                    break

            # Check if we've hit a target second
            current_time = current_time_ns / 1_000_000_000.0
            time_struct = gmtime(current_time)
            current_second = time_struct.tm_sec

            if current_second in second_matches:
                return datetime.fromtimestamp(
                    current_time_ns / 1_000_000_000.0, tz=timezone.utc
                )

"""Problem 2: Event Scheduler."""

import heapq
from typing import List, Tuple

Event = Tuple[int, int]


def can_attend_all(events: List[Event]) -> bool:
    """True if no two events overlap. end == next start is allowed."""
    ordered = sorted(events)
    for (_, prev_end), (next_start, _) in zip(ordered, ordered[1:]):
        if next_start < prev_end:
            return False
    return True


def min_rooms_required(events: List[Event]) -> int:
    """Sort by start; a min-heap holds the end times of rooms in use.

    Before placing an event, free every room whose meeting ended at or
    before this start. The largest heap size seen is the answer.
    """
    heap = []
    rooms = 0
    for start, end in sorted(events):
        while heap and heap[0] <= start:
            heapq.heappop(heap)
        heapq.heappush(heap, end)
        rooms = max(rooms, len(heap))
    return rooms


def assign_rooms(events: List[Event]) -> List[Tuple[Event, str]]:
    """Discussion Q3: label each event with a room ("Room A", "Room B", ...).

    Heap entries are (end_time, room_id). Freed room ids go back into a
    second min-heap so the lowest free room is always reused first.
    Returns pairs in the original input order.
    """
    order = sorted(range(len(events)), key=lambda i: events[i])
    busy = []          # (end_time, room_id)
    free = []          # room ids that were opened and are now free
    next_room = 0
    result = [None] * len(events)

    for i in order:
        start, end = events[i]
        while busy and busy[0][0] <= start:
            _, room = heapq.heappop(busy)
            heapq.heappush(free, room)
        if free:
            room = heapq.heappop(free)
        else:
            room = next_room
            next_room += 1
        heapq.heappush(busy, (end, room))
        result[i] = (events[i], _room_name(room))
    return result


def _room_name(n: int) -> str:
    # 0 -> A, 25 -> Z, 26 -> AA, ...
    name = ""
    n += 1
    while n:
        n, r = divmod(n - 1, 26)
        name = chr(65 + r) + name
    return "Room " + name

# Data Structures & Systems Design Assignment

**Chinthan Shetty** · AI / Multi-Agent Systems Intern, Avaloka (Guruvai Sciences)

Language: Python 3. Unit tests for every function are in `test_solutions.py` (8 tests, all passing).

---

## Problem 1: LRU Cache

### Approach

An LRU cache has to do two things quickly. It has to find a value by its key, and it has to keep track of which key was used least recently so it can be evicted.

No single standard structure does both in O(1):

- A **hash map** finds a key in O(1), but it has no idea of order, so finding the least recently used entry means scanning everything.
- A **linked list** keeps order and lets me move or remove a node in O(1) once I have a pointer to it, but finding a key in the list is O(n).

So I use both. The hash map stores `key -> node`, and each node lives in a **doubly linked list** ordered by recency: the front is the most recently used, the back the least.

- **get(key):** look up the node in the map. If it's missing, return -1. Otherwise unlink the node and move it to the front, then return its value.
- **put(key, value):** if the key exists, update the value and move the node to the front. If it's new and the cache is full, drop the node at the back of the list (that's the LRU entry) and delete its key from the map, then insert the new node at the front.

**Why doubly linked?** To unlink a node in O(1) I need its predecessor. With a singly linked list I'd have to walk from the head to find it, which makes the operation O(n).

**Why store the key inside the node?** On eviction I only have the tail node. The node needs its own key so I can delete the matching map entry without searching.

**Sentinel head and tail nodes** mean the list is never empty, so insert and remove need no `if node is None` special cases. That removes a common source of bugs.

### Code

```python
class _Node:
    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("capacity must be a positive integer")
        self.capacity = capacity
        self._map = {}
        self._head = _Node()          # sentinel: head.next = most recent
        self._tail = _Node()          # sentinel: tail.prev = least recent
        self._head.next = self._tail
        self._tail.prev = self._head

    def _remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_front(self, node):
        node.prev = self._head
        node.next = self._head.next
        self._head.next.prev = node
        self._head.next = node

    def get(self, key):
        node = self._map.get(key)
        if node is None:
            return -1
        self._remove(node)
        self._add_to_front(node)
        return node.value

    def put(self, key, value):
        node = self._map.get(key)
        if node is not None:
            node.value = value
            self._remove(node)
            self._add_to_front(node)
            return
        if len(self._map) == self.capacity:
            lru = self._tail.prev
            self._remove(lru)
            del self._map[lru.key]
        node = _Node(key, value)
        self._map[key] = node
        self._add_to_front(node)
```

---

## Problem 2: Event Scheduler

### Approach: `can_attend_all`

One person can attend everything only if no two events overlap. After sorting by start time, any overlap has to show up between two neighbours in the sorted list. If event *i+1* starts before event *i* ends, they clash. I check every adjacent pair. The comparison is strict (`next_start < prev_end`), so an event ending at 10 and the next starting at 10 is allowed, as the constraints require.

### Approach: `min_rooms_required`

The number of rooms needed equals the largest number of meetings running at the same moment. To track that, I process events in order of start time and keep a **min-heap of end times** for the rooms currently in use. The heap's top is always the room that frees up soonest.

For each event:

1. While the earliest-ending meeting has ended by now (`end <= start`), pop it; that room is free again. Using `<=` is what makes back-to-back meetings share a room.
2. Push this event's end time; it now occupies a room.
3. The heap size is the number of rooms busy at this moment. The answer is the largest size seen.

Example `[(0,30), (5,10), (15,20)]`: at 0 the heap is {30}. At 5, 30 hasn't ended, so the heap is {10, 30}: 2 rooms. At 15, 10 has ended and is popped, then 20 is pushed: {20, 30}, still 2. Answer: **2**.

### Code

```python
import heapq

def can_attend_all(events):
    ordered = sorted(events)
    for (_, prev_end), (next_start, _) in zip(ordered, ordered[1:]):
        if next_start < prev_end:
            return False
    return True


def min_rooms_required(events):
    heap = []      # end times of rooms currently in use
    rooms = 0
    for start, end in sorted(events):
        while heap and heap[0] <= start:
            heapq.heappop(heap)
        heapq.heappush(heap, end)
        rooms = max(rooms, len(heap))
    return rooms
```

---

## Final Discussion & Analysis

### 1. Time & Space Complexity

*n* = number of events, *c* = cache capacity.

| Function | Time | Space | Why |
|---|---|---|---|
| `LRUCache.get` | O(1) | O(1) extra | One hash lookup plus a constant number of pointer updates |
| `LRUCache.put` | O(1) | O(1) extra | Hash lookup or insert, a pointer move, and at most one eviction from the tail |
| `LRUCache` overall | n/a | O(c) | At most *c* map entries and *c* list nodes |
| `can_attend_all` | O(n log n) | O(n) | Sorting dominates; the scan is O(n). The sorted copy is O(n); sorting in place would leave only Timsort's buffer |
| `min_rooms_required` | O(n log n) | O(n) | Sort is O(n log n); each event is pushed and popped at most once, each costing O(log n) |
| `assign_rooms` (Q3) | O(n log n) | O(n) | Same as above, plus a second heap of free room ids |

Hash-map operations are O(1) on average. A pathological hash collision pattern could degrade a single lookup, which is standard for any hash-based design.

### 2. Trade-offs: why a hash map plus a doubly linked list?

Each structure fixes the other's weakness:

- The **hash map** answers "where is key *k*?" in O(1) but has no ordering.
- The **doubly linked list** answers "what's least recent?" (the tail) and "move this to most recent" in O(1), but can't find a key without scanning.

The map stores pointers into the list, so every operation becomes one lookup plus a few pointer updates.

The alternatives are worse on at least one operation:

- **An array or plain list ordered by recency:** moving an element to the front shifts everything, O(n).
- **A map of key → last-used timestamp:** get and put are O(1), but finding the oldest entry to evict is an O(n) scan.
- **A min-heap on timestamps:** eviction is O(log n), and every `get` has to update a key's priority, which is also O(log n) and awkward to do.

The cost of the chosen design is **memory and complexity**. Every entry carries two extra pointers and a copy of its key, and the pointer manipulation is easy to get wrong. That's why I used sentinel nodes. In production Python I'd likely use `collections.OrderedDict`, which is this same structure implemented in C, with `move_to_end()` and `popitem(last=False)`. I wrote it by hand here to show the mechanics.

### 3. Future proofing: assigning specific rooms

`min_rooms_required` only counts rooms. To name them, the heap has to remember **which** room each meeting is in, so I store `(end_time, room_id)` instead of just `end_time`. I also keep a second min-heap of **free room ids** so the lowest-numbered free room (Room A before Room B) gets reused first, which keeps the assignments predictable.

For each event in start-time order:

1. Pop every busy room whose meeting has ended (`end <= start`) and push its id onto the free heap.
2. Take the smallest free id. If none is free, open a new room (`next_room += 1`).
3. Push `(end, room_id)` onto the busy heap and record the assignment.

The number of distinct rooms opened always equals `min_rooms_required`, so this uses no extra rooms. It's still O(n log n).

```python
def assign_rooms(events):
    order = sorted(range(len(events)), key=lambda i: events[i])
    busy, free, next_room = [], [], 0
    result = [None] * len(events)
    for i in order:
        start, end = events[i]
        while busy and busy[0][0] <= start:
            _, room = heapq.heappop(busy)
            heapq.heappush(free, room)
        if free:
            room = heapq.heappop(free)
        else:
            room, next_room = next_room, next_room + 1
        heapq.heappush(busy, (end, room))
        result[i] = (events[i], _room_name(room))   # 0 -> "Room A", 26 -> "Room AA"
    return result
```

Result for `[(0,30), (5,10), (10,15), (15,20)]`: (0,30) → Room A; the other three → Room B.

A real platform would extend this further:

- **Rooms with properties** such as capacity or video equipment: check each free room against the event's requirements instead of taking any free room.
- **A fixed set of physical rooms:** when no room is free, the event can't be placed, so return a conflict instead of opening a new room.
- **Live booking,** where events arrive one at a time: keep a sorted interval structure per room (for example an interval tree) so a new booking can be checked in O(log n) without re-running the whole schedule.

### 4. Concurrency: making the LRU cache thread-safe

The key point is that **`get` is also a write**. It moves a node to the front of the list. If two threads run `_remove` / `_add_to_front` at the same time, they can leave `prev` and `next` pointers inconsistent. That breaks the list in ways that are hard to debug, such as lost nodes, cycles, or the map and list disagreeing about size. Python's GIL doesn't prevent this, because each operation spans several bytecode steps.

**The simplest correct fix** is one mutex around the whole of each public method:

```python
import threading

class ThreadSafeLRUCache(LRUCache):
    def __init__(self, capacity):
        super().__init__(capacity)
        self._lock = threading.Lock()

    def get(self, key):
        with self._lock:
            return super().get(key)

    def put(self, key, value):
        with self._lock:
            super().put(key, value)
```

The lock has to cover the **map and the list together**. Locking them separately would let another thread see a key in the map whose node is half-unlinked. My test runs 8 threads doing 16,000 mixed operations and then checks that the list length still matches the map size.

**A read-write lock doesn't help much here,** because every `get` modifies the recency order, so there are almost no pure reads. That's a common mistake.

**If one lock becomes a bottleneck** under heavy contention:

- **Sharding:** split the cache into N independent LRU caches, each with its own lock, and route by `hash(key) % N`. Contention drops by roughly N times. The cost is that eviction becomes "least recently used *within a shard*", an approximation of global LRU that is usually fine in practice.
- **Batched recency updates** (the approach used by Java's Caffeine library): `get` reads the value without the list lock and logs "key was accessed" into a lock-free buffer. That buffer is replayed onto the list in batches. Reads stop blocking each other, at the cost of the order being briefly stale.
- **Approximate LRU** such as the CLOCK algorithm, or Redis-style sampling, which evicts the oldest of a few randomly sampled keys. These avoid maintaining a strict order on every read.

In a distributed or multi-process setting, the in-process lock no longer applies. You'd use an external cache such as Redis with its own eviction policy, or route each key to a single owner process.

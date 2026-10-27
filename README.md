# Avaloka Assignment: Data Structures & Systems Design

My solutions to the take-home assignment for the AI / Multi-Agent Systems Intern role at Avaloka (Guruvai Sciences).

The full write-up (approach for each problem plus the Final Discussion answers) is in [writeup.md](writeup.md).

## Contents

| File | What it contains |
|---|---|
| [lru_cache.py](lru_cache.py) | Problem 1: `LRUCache` with O(1) `get` / `put` (hash map + doubly linked list), and `ThreadSafeLRUCache` for the concurrency question |
| [event_scheduler.py](event_scheduler.py) | Problem 2: `can_attend_all`, `min_rooms_required`, and `assign_rooms` for the room-naming question |
| [test_solutions.py](test_solutions.py) | Unit tests for every function, including a multi-threaded stress test |
| [writeup.md](writeup.md) | Approach, code walkthrough, complexity analysis and discussion |

## Running the tests

Python 3.8+ with no third-party dependencies.

```bash
python3 -m unittest -v test_solutions
```

## Complexity at a glance

| Function | Time | Space |
|---|---|---|
| `LRUCache.get` / `put` | O(1) | O(capacity) total |
| `can_attend_all` | O(n log n) | O(n) |
| `min_rooms_required` | O(n log n) | O(n) |
| `assign_rooms` | O(n log n) | O(n) |

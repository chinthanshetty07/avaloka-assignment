"""Problem 1: LRU Cache with O(1) get and put."""

import threading


class _Node:
    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """Hash map (key -> node) + doubly linked list ordered by recency.

    head.next is the most recently used node, tail.prev the least recently used.
    head and tail are sentinels, so insert/remove never have to check for None.
    """

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("capacity must be a positive integer")
        self.capacity = capacity
        self._map = {}
        self._head = _Node()
        self._tail = _Node()
        self._head.next = self._tail
        self._tail.prev = self._head

    def _remove(self, node: _Node) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_front(self, node: _Node) -> None:
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

    def put(self, key, value) -> None:
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

    def __len__(self):
        return len(self._map)


class ThreadSafeLRUCache(LRUCache):
    """Same cache, with one lock around each operation.

    get() mutates the list too (it moves the node to the front), so reads
    need the lock as well, not only writes.
    """

    def __init__(self, capacity: int):
        super().__init__(capacity)
        self._lock = threading.Lock()

    def get(self, key):
        with self._lock:
            return super().get(key)

    def put(self, key, value) -> None:
        with self._lock:
            super().put(key, value)

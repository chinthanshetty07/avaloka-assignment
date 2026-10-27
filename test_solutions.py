import threading
import unittest

from event_scheduler import assign_rooms, can_attend_all, min_rooms_required
from lru_cache import LRUCache, ThreadSafeLRUCache


class TestLRU(unittest.TestCase):
    def test_basic_eviction(self):
        c = LRUCache(2)
        c.put(1, 1)
        c.put(2, 2)
        self.assertEqual(c.get(1), 1)   # 1 is now most recent
        c.put(3, 3)                     # evicts 2
        self.assertEqual(c.get(2), -1)
        c.put(4, 4)                     # evicts 1
        self.assertEqual(c.get(1), -1)
        self.assertEqual(c.get(3), 3)
        self.assertEqual(c.get(4), 4)

    def test_update_refreshes_recency(self):
        c = LRUCache(2)
        c.put(1, 1)
        c.put(2, 2)
        c.put(1, 10)                    # update, 1 becomes most recent
        c.put(3, 3)                     # evicts 2
        self.assertEqual(c.get(1), 10)
        self.assertEqual(c.get(2), -1)
        self.assertEqual(len(c), 2)

    def test_capacity_one(self):
        c = LRUCache(1)
        c.put("a", 1)
        c.put("b", 2)
        self.assertEqual(c.get("a"), -1)
        self.assertEqual(c.get("b"), 2)

    def test_invalid_capacity(self):
        with self.assertRaises(ValueError):
            LRUCache(0)

    def test_thread_safe_under_load(self):
        c = ThreadSafeLRUCache(50)

        def worker(base):
            for i in range(2000):
                c.put((base + i) % 200, i)
                c.get((base + i * 7) % 200)

        threads = [threading.Thread(target=worker, args=(t * 13,)) for t in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(len(c), 50)
        # list length must match map size if nothing got corrupted
        n, node = 0, c._head.next
        while node is not c._tail:
            n += 1
            node = node.next
        self.assertEqual(n, 50)


class TestScheduler(unittest.TestCase):
    def test_can_attend(self):
        self.assertTrue(can_attend_all([(9, 10), (10, 11), (11, 12)]))
        self.assertFalse(can_attend_all([(9, 11), (10, 12)]))
        self.assertTrue(can_attend_all([]))
        self.assertTrue(can_attend_all([(11, 12), (9, 10)]))  # unsorted input

    def test_min_rooms(self):
        self.assertEqual(min_rooms_required([(9, 10), (10, 11), (11, 12)]), 1)
        self.assertEqual(min_rooms_required([(0, 30), (5, 10), (15, 20)]), 2)
        self.assertEqual(min_rooms_required([(1, 5), (2, 6), (3, 7), (4, 8)]), 4)
        self.assertEqual(min_rooms_required([(1, 2), (1, 2), (2, 3)]), 2)
        self.assertEqual(min_rooms_required([]), 0)

    def test_assign_rooms(self):
        events = [(0, 30), (5, 10), (15, 20), (10, 15)]
        got = dict(assign_rooms(events))
        self.assertEqual(got[(0, 30)], "Room A")
        self.assertEqual(got[(5, 10)], "Room B")
        self.assertEqual(got[(10, 15)], "Room B")
        self.assertEqual(got[(15, 20)], "Room B")
        self.assertEqual(len(set(got.values())), min_rooms_required(events))


if __name__ == "__main__":
    unittest.main()

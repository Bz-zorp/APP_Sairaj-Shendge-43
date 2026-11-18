
import gc
import sys
import time
import weakref
import tracemalloc


def section(title):
    print(f"\n{'=' * 8} {title} {'=' * 8}")


class Node:
    """A tiny object that announces when it is destroyed."""

    def __init__(self, name):
        self.name = name
        self.other = None

    def __del__(self):
        print(f"   [__del__] {self.name} destroyed")


def exp1_reference_counting():
    section("1. Reference counting: instant cleanup")

    a = Node("A")
    print("refcount of A:", sys.getrefcount(a))

    b = a
    print("after b = a, refcount:", sys.getrefcount(a))

    del a
    print("after del a, refcount:", sys.getrefcount(b))

    print("deleting the last name...")
    del b
    print("(destroyed immediately, no gc needed)")


def exp2_cycle_and_manual_collect():
    section("2. Reference cycle until gc.collect()")

    gc.collect()
    gc.disable()

    print("gc enabled?", gc.isenabled())

    x, y = Node("X"), Node("Y")
    x.other, y.other = y, x

    del x, y

    print("deleted both names. Nothing printed => still in memory")

    found = gc.collect()
    print(f"gc.collect() returned {found}")

    gc.enable()

def exp3_thresholds_counts_stats():
    section("3. Thresholds, counts and statistics")

    print("get_threshold():", gc.get_threshold())
    print("get_count():", gc.get_count())

    print("get_stats():")
    s = gc.get_stats()[0]

    print("collections =", s["collections"])
    print("collected =", s["collected"])
    print("uncollectable =", s["uncollectable"])


# EXPERIMENT 4: Automatic collection
def exp4_automatic_trigger():
    section("4. Automatic collection triggered by threshold")

    events = []

    def watcher(phase, info):
        if phase == "stop":
            events.append(
                (info["generation"], info["collected"])
            )

    gc.callbacks.append(watcher)

    old = gc.get_threshold()

    try:
        gc.collect()
        gc.set_threshold(50, 5, 5)
        events.clear()

        for _ in range(300):
            a, b = [], []
            a.append(b)
            b.append(a)

        print(f"With threshold0=50, gc ran {len(events)} times.")
        print("First few runs:", events[:5])

    finally:
        gc.set_threshold(*old)
        gc.callbacks.remove(watcher)



def exp5_generations():
    section("5. Generations: young objects grow old")

    gc.collect()

    keeper = [Node("K")]
    keeper[0].other = keeper

    print("BEFORE collect(0):",
          [len(gc.get_objects(g)) for g in range(3)])

    gc.collect(0)

    print("AFTER collect(0):",
          [len(gc.get_objects(g)) for g in range(3)])

    gc.collect(1)

    print("AFTER collect(1):",
          [len(gc.get_objects(g)) for g in range(3)])

    print("Young objects surviving are promoted.")

    keeper[0].other = None
    del keeper



def exp6_memory_effect():
    section("6. Memory effect of cycles")

    gc.collect()
    gc.disable()

    tracemalloc.start()

    base = tracemalloc.get_traced_memory()[0]

    for _ in range(20000):
        a, b = {}, {}
        a["b"], b["a"] = b, a

    del a, b

    leaked = tracemalloc.get_traced_memory()[0] - base

    n = gc.collect()

    after = tracemalloc.get_traced_memory()[0] - base

    tracemalloc.stop()
    gc.enable()

    print(f"Memory held by cycles: {leaked / 1024:.1f} KiB")
    print(f"gc.collect() freed {n} objects")
    print(f"Memory after collect: {after / 1024:.1f} KiB")



def exp7_debug_saveall():
    section("7. DEBUG_SAVEALL: inspect garbage")

    gc.collect()

    gc.set_debug(gc.DEBUG_SAVEALL)

    p, q = [1], [2]
    p.append(q)
    q.append(p)

    del p, q

    gc.collect()

    print("gc.garbage now holds:", gc.garbage)

    gc.set_debug(0)
    gc.garbage.clear()

    gc.collect()



def exp8_tracking_and_weakref():
    section("8. is_tracked() and weak references")

    samples = [
        ("int 5", 5),
        ("string", "hi"),
        ("list", [1]),
        ("empty dict", {}),
        ("dict with list", {"k": [1]}),
        ("tuple of ints", (1, 2)),
        ("Node object", Node("T"))
    ]

    for label, obj in samples:
        print(f"{label:<16} tracked by gc? {gc.is_tracked(obj)}")

    n = Node("W")
    ref = weakref.ref(n)

    print("weakref alive?", ref() is not None)

    del n

    print("after del, weakref alive?", ref() is not None)


def exp9_freeze():
    section("9. gc.freeze(): park long-lived objects")

    gc.collect()

    print("frozen before:", gc.get_freeze_count())

    gc.freeze()

    print("frozen after:", gc.get_freeze_count())

    gc.unfreeze()

    print("after unfreeze:", gc.get_freeze_count())

def exp10_timing():
    section("10. Cost of automatic garbage collection")

    def work():
        data = []

        for i in range(400000):
            data.append([i])

        return len(data)

    results = {}

    for label, enabled in (
        ("gc enabled", True),
        ("gc disabled", False)
    ):
        gc.collect()

        if enabled:
            gc.enable()
        else:
            gc.disable()

        t = time.perf_counter()

        work()

        results[label] = time.perf_counter() - t

        gc.enable()

        print(f"{label}: {results[label] * 1000:.1f} ms")

    print("Timings vary by machine and Python version.")


if __name__ == "__main__":

    print("Python", sys.version.split()[0])

    exp1_reference_counting()
    exp2_cycle_and_manual_collect()
    exp3_thresholds_counts_stats()
    exp4_automatic_trigger()
    exp5_generations()
    exp6_memory_effect()
    exp7_debug_saveall()
    exp8_tracking_and_weakref()
    exp9_freeze()
    exp10_timing()

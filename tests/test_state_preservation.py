"""State-preservation mocks for Botile.

Run from the project root:

    python3 tests/test_state_preservation.py

These tests exercise the plugin's radius/mark state machine directly. They do
not load Android or prove rendering.
"""

import importlib.util
import sys
import threading
import types
from importlib.machinery import SourceFileLoader

PLUGIN = "Botile.plugin"
MARKER = "botile:bot"


class FakeHookFilter:
    @staticmethod
    def Condition(expression):
        return ("condition", expression)

    @staticmethod
    def Or(*filters):
        return ("or", filters)

    @staticmethod
    def ArgumentIsInstanceOf(index, clazz):
        return ("instance", index, clazz)


class MethodHook:
    pass


class BasePlugin:
    id = "botile"


base_plugin = types.ModuleType("base_plugin")
base_plugin.BasePlugin = BasePlugin
base_plugin.MethodHook = MethodHook
base_plugin.HookFilter = FakeHookFilter

hook_utils = types.ModuleType("hook_utils")
hook_utils.find_class = lambda name: None

android_utils = types.ModuleType("android_utils")
android_utils.run_on_ui_thread = lambda fn, delay=0: fn()

sys.modules["base_plugin"] = base_plugin
sys.modules["hook_utils"] = hook_utils
sys.modules["android_utils"] = android_utils

loader = SourceFileLoader("botile_state_test", PLUGIN)
spec = importlib.util.spec_from_loader("botile_state_test", loader)
module = importlib.util.module_from_spec(spec)
loader.exec_module(module)


class FakeArrays:
    @staticmethod
    def copyOf(values, length):
        result = [0] * length
        for index in range(min(length, len(values))):
            result[index] = int(values[index])
        return result


class FakeWeakHashMap:
    def __init__(self):
        self.data = {}

    def get(self, key):
        return self.data.get(key)

    def put(self, key, value):
        self.data[key] = value

    def remove(self, key):
        self.data.pop(key, None)

    def containsKey(self, key):
        return key in self.data

    def keySet(self):
        return list(self.data.keys())

    def clear(self):
        self.data.clear()


class FakeParent:
    def getClass(self):
        return types.SimpleNamespace(
            getName=lambda: "org.telegram.ui.Cells.DialogCell"
        )


class FakeReceiver:
    def __init__(self, corners=(26, 26, 26, 26), mark=None):
        self.corners = list(corners)
        self.mark = mark
        self.corners_applied = False
        self.invalidations = 0

    def getRoundRadius(self):
        return list(self.corners)

    def setRoundRadius(self, value):
        if isinstance(value, (list, tuple)):
            self.corners = [int(item) for item in value]
        else:
            self.corners = [int(value)] * 4

    def getMark(self):
        return self.mark

    def setMark(self, value):
        self.mark = value

    def setAvatarCornersApplied(self, value):
        self.corners_applied = bool(value)

    def getImageWidth(self):
        return 0.0

    def getParentView(self):
        return FakeParent()

    def invalidate(self):
        self.invalidations += 1


def make_plugin():
    plugin = module.BotilePlugin()
    plugin.id = "botile"
    plugin.logs = []
    plugin.log = plugin.logs.append
    plugin._radius_px = 33
    plugin._arrays = FakeArrays
    plugin._baselines = FakeWeakHashMap()
    plugin._applied = FakeWeakHashMap()
    plugin._marks = FakeWeakHashMap()
    plugin._mark_nulls = FakeWeakHashMap()
    plugin._local = threading.local()
    plugin._lock = threading.RLock()
    plugin._firsts = set()
    plugin._errors = set()
    plugin._stats = {
        "binds": 0, "bots": 0, "nonbots": 0, "overrides": 0,
        "verified": 0, "clears": 0, "custom": 0, "dialog": 0,
        "unknown_parent": 0,
    }
    return plugin


def test_zero_baseline_round_trip():
    plugin = make_plugin()
    receiver = FakeReceiver((0, 0, 0, 0))
    plugin._apply_bot(receiver, "test")
    assert receiver.corners == [33, 33, 33, 33]
    plugin._clear_bot(receiver, "test")
    assert receiver.corners == [0, 0, 0, 0], receiver.corners


def test_asymmetric_baseline_round_trip():
    plugin = make_plugin()
    receiver = FakeReceiver((10, 20, 30, 40))
    plugin._apply_bot(receiver, "test")
    assert receiver.corners == [18, 18, 18, 18], receiver.corners
    plugin._clear_bot(receiver, "test")
    assert receiver.corners == [10, 20, 30, 40], receiver.corners


def test_zero_baseline_unload():
    plugin = make_plugin()
    receiver = FakeReceiver((0, 0, 0, 0))
    plugin._apply_bot(receiver, "test")
    plugin._restore_all()
    assert receiver.corners == [0, 0, 0, 0], receiver.corners


def test_asymmetric_baseline_unload():
    plugin = make_plugin()
    receiver = FakeReceiver((5, 15, 25, 35))
    plugin._apply_bot(receiver, "test")
    plugin._restore_all()
    assert receiver.corners == [5, 15, 25, 35], receiver.corners


def test_existing_mark_restored():
    plugin = make_plugin()
    receiver = FakeReceiver(mark="external-before")
    plugin._apply_bot(receiver, "test")
    assert receiver.mark == MARKER
    plugin._clear_bot(receiver, "test")
    assert receiver.mark == "external-before", receiver.mark


def test_null_mark_restored():
    plugin = make_plugin()
    receiver = FakeReceiver(mark=None)
    plugin._apply_bot(receiver, "test")
    assert receiver.mark == MARKER
    plugin._clear_bot(receiver, "test")
    assert receiver.mark is None


def test_later_external_mark_not_clobbered():
    plugin = make_plugin()
    receiver = FakeReceiver(mark="external-before")
    plugin._apply_bot(receiver, "test")
    receiver.mark = "later-external"
    plugin._clear_bot(receiver, "test")
    assert receiver.mark == "later-external", receiver.mark


def test_unload_restores_mark():
    plugin = make_plugin()
    receiver = FakeReceiver(mark="external-unload")
    plugin._apply_bot(receiver, "test")
    plugin._restore_all()
    assert receiver.mark == "external-unload", receiver.mark


def test_unload_leaves_later_external_mark():
    plugin = make_plugin()
    receiver = FakeReceiver(mark="external-unload")
    plugin._apply_bot(receiver, "test")
    receiver.mark = "later-unload"
    plugin._restore_all()
    assert receiver.mark == "later-unload", receiver.mark


def main():
    tests = [
        value for name, value in sorted(globals().items())
        if name.startswith("test_") and callable(value)
    ]
    for test in tests:
        test()
    print("state-preservation mocks passed: %d" % len(tests))


if __name__ == "__main__":
    main()

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


class FakeRectF:
    def __init__(self):
        self.left = self.top = self.right = self.bottom = 0.0

    def set(self, left, top, right, bottom):
        self.left, self.top, self.right, self.bottom = left, top, right, bottom

    def width(self):
        return self.right - self.left

    def height(self):
        return self.bottom - self.top


class FakePaint:
    def __init__(self):
        self.color = 0
        self.stroke_width = 0.0
        self.style = None
        self.anti_alias = False

    def setAntiAlias(self, value):
        self.anti_alias = bool(value)

    def setStyle(self, value):
        self.style = value

    def setStrokeWidth(self, value):
        self.stroke_width = float(value)

    def setColor(self, value):
        self.color = int(value)


class FakeCanvas:
    def __init__(self):
        self.calls = []

    def drawRoundRect(self, rect, rx, ry, paint):
        self.calls.append((rect, rx, ry, paint))


class FakeTheme:
    key_windowBackgroundWhiteBlackText = 7

    @staticmethod
    def getColor(key):
        assert key == FakeTheme.key_windowBackgroundWhiteBlackText
        return 0xFF102030

    @staticmethod
    def multAlpha(color, multiply):
        alpha = int((color >> 24) * multiply) & 0xFF
        return (alpha << 24) | (color & 0xFFFFFF)


class FakeDrawReceiver(FakeReceiver):
    def __init__(self, corners=(11, 11, 11, 11), mark=MARKER):
        super().__init__(corners=corners, mark=mark)
        self.image_x = 10.0
        self.image_y = 20.0
        self.image_w = 100.0
        self.image_h = 100.0
        self.alpha = 1.0
        self.current_alpha = 1.0

    def getImageX(self):
        return self.image_x

    def getImageY(self):
        return self.image_y

    def getImageWidth(self):
        return self.image_w

    def getImageHeight(self):
        return self.image_h

    def getAlpha(self):
        return self.alpha

    def getCurrentAlpha(self):
        return self.current_alpha


class FakeParam:
    def __init__(self, obj, args, result=True):
        self.thisObject = obj
        self.args = args
        self._result = result

    def getResult(self):
        return self._result


def make_border_plugin():
    plugin = make_plugin()
    plugin._border_paint = FakePaint()
    plugin._border_rect = FakeRectF()
    plugin._border_stroke = 3.0
    plugin._theme = FakeTheme
    return plugin


def test_border_draws_inside_bounds_for_bot():
    plugin = make_border_plugin()
    receiver = FakeDrawReceiver()
    canvas = FakeCanvas()
    plugin._draw_bot_border(canvas, receiver)
    assert len(canvas.calls) == 1
    rect, rx, ry, paint = canvas.calls[0]
    assert (rect.left, rect.top, rect.right, rect.bottom) == (11.5, 21.5, 108.5, 118.5)
    assert rx == 11.0 and ry == 11.0
    assert paint.stroke_width == 3.0
    assert (paint.color >> 24) == int(0xFF * 0.45)


def test_border_skips_unmarked_and_transparent_avatars():
    plugin = make_border_plugin()
    canvas = FakeCanvas()
    unmarked = FakeDrawReceiver(mark=None)
    plugin._draw_bot_border(canvas, unmarked)
    transparent = FakeDrawReceiver()
    transparent.alpha = 0.0
    plugin._draw_bot_border(canvas, transparent)
    assert canvas.calls == []


def test_border_hook_skips_background_holder_and_failed_draw():
    plugin = make_border_plugin()
    receiver = FakeDrawReceiver()
    hook = module._BorderDrawHook(plugin)
    canvas = FakeCanvas()
    hook.after_hooked_method(FakeParam(receiver, [canvas, object()], True))
    hook.after_hooked_method(FakeParam(receiver, [canvas, None], False))
    assert canvas.calls == []
    hook.after_hooked_method(FakeParam(receiver, [canvas, None], True))
    assert len(canvas.calls) == 1


class FakeReflectedParameter:
    def __init__(self, name):
        self.name = name

    def getName(self):
        return self.name


class FakeReflectedMethod:
    def __init__(self, name, parameter_names):
        self.name = name
        self.parameters = [FakeReflectedParameter(value) for value in parameter_names]
        self.accessible = False

    def getName(self):
        return self.name

    def getParameterTypes(self):
        return self.parameters

    def setAccessible(self, value):
        self.accessible = bool(value)


class FakeJavaClass:
    """A java.lang.Class instance carrying reflected methods."""

    def __init__(self, methods):
        self.methods = methods

    def getDeclaredMethods(self):
        return self.methods


class FakeRuntimeClassProxy:
    """A jclass wrapper: getClass() returns the Class, no Class methods."""

    def __init__(self, methods):
        self.java_class = FakeJavaClass(methods)

    def getClass(self):
        return self.java_class


def test_class_proxy_normalization():
    proxy = FakeRuntimeClassProxy([])
    assert not hasattr(proxy, "getDeclaredMethods")
    assert module._as_java_class(proxy) is proxy.java_class


def test_exact_method_overload_resolution():
    wrong = FakeReflectedMethod("setImage", ("java.lang.String",))
    expected = FakeReflectedMethod("setImage", ("java.lang.String", "int"))
    clazz = FakeRuntimeClassProxy([wrong, expected])
    found = module._find_declared_method(
        clazz, "setImage", ("java.lang.String", "int")
    )
    assert found is expected
    assert expected.accessible
    assert not wrong.accessible


def test_bind_and_dialog_signatures_via_runtime_proxy():
    bind = FakeReflectedMethod(
        "setForUserOrChat",
        (
            "org.telegram.tgnet.TLObject",
            "android.graphics.drawable.Drawable",
            "java.lang.Object",
            "boolean",
            "int",
            "boolean",
        ),
    )
    update = FakeReflectedMethod("update", ("int", "boolean"))
    draw = FakeReflectedMethod(
        "draw",
        (
            "android.graphics.Canvas",
            "org.telegram.messenger.ImageReceiver$BackgroundThreadDrawHolder",
        ),
    )
    proxy = FakeRuntimeClassProxy([bind, update, draw])
    assert module._find_declared_method(
        proxy,
        "setForUserOrChat",
        (
            "org.telegram.tgnet.TLObject",
            "android.graphics.drawable.Drawable",
            "java.lang.Object",
            "boolean",
            "int",
            "boolean",
        ),
    ) is bind
    assert module._find_declared_method(
        proxy, "update", ("int", "boolean")
    ) is update
    assert module._find_declared_method(
        proxy,
        "draw",
        (
            "android.graphics.Canvas",
            "org.telegram.messenger.ImageReceiver$BackgroundThreadDrawHolder",
        ),
    ) is draw


def test_missing_method_overload_returns_none():
    clazz = FakeRuntimeClassProxy([FakeReflectedMethod("update", ("int",))])
    assert module._find_declared_method(
        clazz, "update", ("int", "boolean")
    ) is None


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

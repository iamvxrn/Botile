"""Host-side state and compatibility checks for Botile.

Run with: python3 tests/test_state_preservation.py
These mocks do not replace an Android device test.
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
        return [int(values[i]) if i < len(values) else 0 for i in range(length)]


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
    plugin._errors = set()
    plugin._first_bind_logged = False
    plugin._unknown_parent_logged = False
    return plugin


def test_radius_round_trip_preserves_zero_and_asymmetric_corners():
    plugin = make_plugin()
    zero = FakeReceiver((0, 0, 0, 0))
    plugin._apply_bot(zero)
    assert zero.corners == [33, 33, 33, 33]
    plugin._clear_bot(zero)
    assert zero.corners == [0, 0, 0, 0]

    asymmetric = FakeReceiver((10, 20, 30, 40))
    plugin._apply_bot(asymmetric)
    assert asymmetric.corners == [18, 18, 18, 18]
    plugin._clear_bot(asymmetric)
    assert asymmetric.corners == [10, 20, 30, 40]


def test_unload_restores_baselines_and_saved_marks():
    plugin = make_plugin()
    zero = FakeReceiver((0, 0, 0, 0), mark="external-zero")
    asymmetric = FakeReceiver((5, 15, 25, 35), mark=None)
    plugin._apply_bot(zero)
    plugin._apply_bot(asymmetric)
    plugin._restore_all()
    assert zero.corners == [0, 0, 0, 0]
    assert asymmetric.corners == [5, 15, 25, 35]
    assert zero.mark == "external-zero"
    assert asymmetric.mark is None


def test_clear_does_not_clobber_a_later_external_mark():
    plugin = make_plugin()
    receiver = FakeReceiver(mark="external-before")
    plugin._apply_bot(receiver)
    receiver.mark = "later-external"
    plugin._clear_bot(receiver)
    assert receiver.mark == "later-external"


def test_startup_hook_summary_logging_does_not_raise():
    plugin = make_plugin()
    plugin._hooks_ok = {
        "radius": True,
        "image": True,
        "border": True,
        "dialog": True,
    }
    plugin._log_hook_summary()
    assert plugin.logs[-1] == (
        "Botile hooks: bind=OK radius=OK image=OK border=OK dialog=OK"
    )


def test_custom_image_clears_bot_state():
    plugin = make_plugin()
    receiver = FakeReceiver((78, 78, 78, 78))
    plugin._apply_bot(receiver)
    assert receiver.mark == MARKER and receiver.corners == [33, 33, 33, 33]
    plugin._on_custom_image(receiver)
    assert receiver.mark is None
    assert receiver.corners == [78, 78, 78, 78]


def test_dialog_fallback_reapplies_only_marked_receivers():
    plugin = make_plugin()
    receiver = FakeReceiver((78, 78, 78, 78))
    cell = types.SimpleNamespace(avatarImage=receiver, invalidations=0)
    cell.invalidate = lambda: setattr(cell, "invalidations", cell.invalidations + 1)
    hook = module._DialogFallbackHook(plugin)

    hook.after_hooked_method(types.SimpleNamespace(thisObject=cell))
    assert receiver.corners == [78, 78, 78, 78]
    assert cell.invalidations == 0

    plugin._apply_bot(receiver)
    receiver.corners = [78, 78, 78, 78]
    hook.after_hooked_method(types.SimpleNamespace(thisObject=cell))
    assert receiver.corners == [33, 33, 33, 33]
    assert cell.invalidations == 1


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

    def setAntiAlias(self, value):
        pass

    def setStyle(self, value):
        pass

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
    def __init__(self, mark=MARKER):
        super().__init__((11, 11, 11, 11), mark=mark)
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


def test_border_draws_inside_bounds_and_skips_non_bots():
    plugin = make_border_plugin()
    canvas = FakeCanvas()
    plugin._draw_border(canvas, FakeDrawReceiver())
    assert len(canvas.calls) == 1
    rect, rx, ry, paint = canvas.calls[0]
    assert (rect.left, rect.top, rect.right, rect.bottom) == (11.5, 21.5, 108.5, 118.5)
    assert rx == 11.0 and ry == 11.0
    assert paint.stroke_width == 3.0
    assert (paint.color >> 24) == int(0xFF * 0.45)

    plugin._draw_border(canvas, FakeDrawReceiver(mark=None))
    transparent = FakeDrawReceiver()
    transparent.alpha = 0.0
    plugin._draw_border(canvas, transparent)
    assert len(canvas.calls) == 1


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
    def __init__(self, methods):
        self.methods = methods

    def getDeclaredMethods(self):
        return self.methods


class FakeRuntimeClassProxy:
    def __init__(self, methods):
        self.java_class = FakeJavaClass(methods)

    def getClass(self):
        return self.java_class


def test_class_proxy_normalization_and_exact_overloads():
    draw = FakeReflectedMethod(
        "draw",
        (
            "android.graphics.Canvas",
            "org.telegram.messenger.ImageReceiver$BackgroundThreadDrawHolder",
        ),
    )
    wrong = FakeReflectedMethod("draw", ("android.graphics.Canvas",))
    proxy = FakeRuntimeClassProxy([draw, wrong])
    assert module._as_java_class(proxy) is proxy.java_class
    found = module._find_declared_method(
        proxy,
        "draw",
        (
            "android.graphics.Canvas",
            "org.telegram.messenger.ImageReceiver$BackgroundThreadDrawHolder",
        ),
    )
    assert found is draw
    assert draw.accessible and not wrong.accessible
    assert module._find_declared_method(proxy, "draw", ("java.lang.String",)) is None


def test_direct_avatar_allowlist_is_narrow():
    assert module._is_direct_avatar_parent(
        "org.telegram.ui.ProfileActivity$AvatarImageView$1"
    )
    assert module._is_direct_avatar_parent(
        "org.telegram.ui.Cells.ProfileSearchCell"
    )
    assert not module._is_direct_avatar_parent(
        "org.telegram.ui.PhotoViewer$XXX"
    )
    assert not module._is_direct_avatar_parent(None)


def test_bind_image_and_dialog_signatures_resolve():
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
    image = FakeReflectedMethod(
        "setImage",
        (
            "org.telegram.messenger.ImageLocation",
            "java.lang.String",
            "org.telegram.messenger.ImageLocation",
            "java.lang.String",
            "org.telegram.messenger.ImageLocation",
            "java.lang.String",
            "android.graphics.drawable.Drawable",
            "long",
            "java.lang.String",
            "java.lang.Object",
            "int",
        ),
    )
    dialog = FakeReflectedMethod("update", ("int", "boolean"))
    proxy = FakeRuntimeClassProxy([bind, image, dialog])
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
    assert module._find_declared_method(proxy, "update", ("int", "boolean")) is dialog
    assert module._find_declared_method(
        proxy,
        "setImage",
        (
            "org.telegram.messenger.ImageLocation",
            "java.lang.String",
            "org.telegram.messenger.ImageLocation",
            "java.lang.String",
            "org.telegram.messenger.ImageLocation",
            "java.lang.String",
            "android.graphics.drawable.Drawable",
            "long",
            "java.lang.String",
            "java.lang.Object",
            "int",
        ),
    ) is image


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

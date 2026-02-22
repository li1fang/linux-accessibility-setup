#!/usr/bin/env python3

import signal
import sys

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, Gtk  # noqa: E402


def _best_effort_hide_cursor(window: Gtk.Window) -> None:
    gdk_window = window.get_window()
    if not gdk_window:
        return
    try:
        cursor = Gdk.Cursor.new_for_display(gdk_window.get_display(), Gdk.CursorType.BLANK_CURSOR)
        gdk_window.set_cursor(cursor)
    except Exception:
        pass


def main() -> int:
    window = Gtk.Window(title="Quiet Black Screen")
    window.set_decorated(False)
    window.set_skip_taskbar_hint(True)
    window.set_skip_pager_hint(True)
    window.set_accept_focus(True)
    window.set_can_focus(True)
    try:
        window.set_keep_above(True)
    except Exception:
        pass

    window.add_events(
        Gdk.EventMask.KEY_PRESS_MASK
        | Gdk.EventMask.BUTTON_PRESS_MASK
        | Gdk.EventMask.POINTER_MOTION_MASK
        | Gdk.EventMask.SCROLL_MASK
        | Gdk.EventMask.TOUCH_MASK
    )

    css = b"""
    window {
      background-color: #000000;
    }
    """
    provider = Gtk.CssProvider()
    provider.load_from_data(css)
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )

    def quit_now(*_args) -> None:
        Gtk.main_quit()

    window.connect("key-press-event", lambda *_args: (quit_now(), True)[1])
    window.connect("button-press-event", lambda *_args: (quit_now(), True)[1])
    window.connect("motion-notify-event", lambda *_args: (quit_now(), True)[1])
    window.connect("scroll-event", lambda *_args: (quit_now(), True)[1])
    window.connect("touch-event", lambda *_args: (quit_now(), True)[1])
    window.connect("delete-event", lambda *_args: (quit_now(), True)[1])

    def on_realize(_w: Gtk.Window) -> None:
        _best_effort_hide_cursor(window)
        try:
            window.fullscreen()
        except Exception:
            pass

    window.connect("realize", on_realize)

    signal.signal(signal.SIGINT, lambda *_args: quit_now())
    signal.signal(signal.SIGTERM, lambda *_args: quit_now())

    window.show_all()
    try:
        window.fullscreen()
    except Exception:
        pass
    try:
        window.present()
    except Exception:
        pass

    Gtk.main()
    return 0


if __name__ == "__main__":
    sys.exit(main())

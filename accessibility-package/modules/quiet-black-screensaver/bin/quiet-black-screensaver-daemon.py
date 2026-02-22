#!/usr/bin/env python3

import errno
import fcntl
import glob
import os
import selectors
import signal
import struct
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple


def _ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class Logger:
    def __init__(self, path: str):
        self._path = path

    def log(self, msg: str) -> None:
        line = f"[{_ts()}] {msg}\n"
        try:
            os.makedirs(os.path.dirname(self._path), exist_ok=True)
            with open(self._path, "a", encoding="utf-8") as f:
                f.write(line)
        except Exception:
            pass
        try:
            sys.stdout.write(line)
            sys.stdout.flush()
        except Exception:
            pass


def _state_dir() -> str:
    xdg_state_home = os.environ.get("XDG_STATE_HOME")
    if xdg_state_home:
        return xdg_state_home
    return os.path.expanduser("~/.local/state")


def _expand_user_value(v: str) -> str:
    return os.path.expandvars(os.path.expanduser(v))


def _load_config_file(path: str) -> None:
    if not path or not os.path.exists(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k and k not in os.environ:
                    os.environ[k] = v
    except Exception:
        pass


def _acquire_lock(lock_path: str, logger: Logger):
    os.makedirs(os.path.dirname(lock_path), exist_ok=True)
    f = open(lock_path, "w", encoding="utf-8")
    try:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as e:
        if e.errno in (errno.EACCES, errno.EAGAIN):
            logger.log(f"lock already held: {lock_path}; exiting")
            sys.exit(2)
        raise
    f.write(str(os.getpid()))
    f.flush()
    return f


def _uniq_realpaths(paths: List[str]) -> List[str]:
    seen: Set[str] = set()
    out: List[str] = []
    for p in paths:
        rp = os.path.realpath(p)
        if rp in seen:
            continue
        seen.add(rp)
        out.append(rp)
    return out


def _discover_input_devices() -> List[str]:
    patterns = [
        "/dev/input/by-id/*-event-kbd",
        "/dev/input/by-id/*-event-mouse",
        "/dev/input/by-path/*-event-kbd",
        "/dev/input/by-path/*-event-mouse",
    ]
    candidates: List[str] = []
    for pat in patterns:
        candidates.extend(glob.glob(pat))
    candidates = _uniq_realpaths([p for p in candidates if os.path.exists(p)])
    if candidates:
        return sorted(candidates)
    return sorted(glob.glob("/dev/input/event*"))


_INPUT_EVENT_SIZE = struct.calcsize("llHHl")


def _has_meaningful_input_event(buf: bytes) -> bool:
    if len(buf) < _INPUT_EVENT_SIZE:
        return False
    n = len(buf) // _INPUT_EVENT_SIZE
    off = 0
    for _ in range(n):
        _sec, _usec, etype, _code, _value = struct.unpack_from("llHHl", buf, off)
        off += _INPUT_EVENT_SIZE
        if etype != 0:
            return True
    return False


class InputMonitor:
    def __init__(self, logger: Logger):
        self._logger = logger
        self._sel = selectors.DefaultSelector()
        self._files: Dict[str, object] = {}

    def close(self) -> None:
        for path in list(self._files.keys()):
            self._remove(path)

    def _remove(self, path: str) -> None:
        f = self._files.pop(path, None)
        if not f:
            return
        try:
            self._sel.unregister(f)
        except Exception:
            pass
        try:
            f.close()
        except Exception:
            pass
        self._logger.log(f"stop watching input: {path}")

    def rescan(self) -> int:
        wanted = set(_discover_input_devices())
        current = set(self._files.keys())

        for path in sorted(current - wanted):
            self._remove(path)

        added = 0
        for path in sorted(wanted - current):
            try:
                fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
                f = os.fdopen(fd, "rb", buffering=0)
                self._sel.register(f, selectors.EVENT_READ, data=path)
                self._files[path] = f
                added += 1
                self._logger.log(f"watching input: {path}")
            except FileNotFoundError:
                continue
            except PermissionError as e:
                self._logger.log(f"no permission to read {path}: {e}")
            except OSError as e:
                self._logger.log(f"failed to open {path}: {e}")
        return added

    def wait_activity(self, timeout_sec: float) -> bool:
        events = self._sel.select(timeout_sec)
        active = False
        for key, _mask in events:
            f = key.fileobj
            path = key.data
            try:
                data = f.read(4096)
                if data and _has_meaningful_input_event(data):
                    active = True
            except OSError as e:
                self._logger.log(f"read error {path}: {e}; removing device")
                self._remove(path)
        return active


class ScreenSaverInhibitor:
    def __init__(self, logger: Logger, enabled: bool):
        self._logger = logger
        self._enabled = enabled
        self._cookie: Optional[int] = None

    def inhibit(self) -> None:
        if not self._enabled or self._cookie is not None:
            return
        try:
            p = subprocess.run(
                [
                    "qdbus6",
                    "org.freedesktop.ScreenSaver",
                    "/ScreenSaver",
                    "org.freedesktop.ScreenSaver.Inhibit",
                    "quiet-black-screensaver",
                    "use black overlay instead of lock screen",
                ],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            out = (p.stdout or "").strip()
            if p.returncode != 0:
                self._logger.log(f"screensaver inhibit failed: rc={p.returncode} out={out}")
                return
            self._cookie = int(out)
            self._logger.log(f"screensaver inhibited: cookie={self._cookie}")
        except Exception as e:
            self._logger.log(f"screensaver inhibit error: {e}")

    def uninhibit(self) -> None:
        if self._cookie is None:
            return
        cookie = self._cookie
        self._cookie = None
        try:
            p = subprocess.run(
                [
                    "qdbus6",
                    "org.freedesktop.ScreenSaver",
                    "/ScreenSaver",
                    "org.freedesktop.ScreenSaver.UnInhibit",
                    str(cookie),
                ],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            out = (p.stdout or "").strip()
            if p.returncode != 0:
                self._logger.log(f"screensaver uninhibit failed: rc={p.returncode} out={out}")
                return
            self._logger.log(f"screensaver uninhibited: cookie={cookie}")
        except Exception as e:
            self._logger.log(f"screensaver uninhibit error: {e}")


@dataclass
class PowerProfileTweak:
    enable: bool
    profile_on_black: str = "power-saver"
    _prev: Optional[str] = None

    def _run(self, args: List[str]) -> Tuple[int, str]:
        try:
            p = subprocess.run(args, check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            return p.returncode, (p.stdout or "").strip()
        except FileNotFoundError:
            return 127, "powerprofilesctl not found"

    def enter(self, logger: Logger) -> None:
        if not self.enable:
            return
        rc, out = self._run(["powerprofilesctl", "get"])
        if rc != 0:
            logger.log(f"power profile read failed: rc={rc} out={out}")
            return
        self._prev = out
        rc, out = self._run(["powerprofilesctl", "set", self.profile_on_black])
        if rc != 0:
            logger.log(f"power profile set failed: rc={rc} out={out}")
        else:
            logger.log(f"power profile set: {self._prev} -> {self.profile_on_black}")

    def exit(self, logger: Logger) -> None:
        if not self.enable:
            return
        if not self._prev:
            return
        rc, out = self._run(["powerprofilesctl", "set", self._prev])
        if rc != 0:
            logger.log(f"power profile restore failed: rc={rc} out={out}")
        else:
            logger.log(f"power profile restored: {self.profile_on_black} -> {self._prev}")
        self._prev = None


class Overlay:
    def __init__(self, overlay_path: str, logger: Logger):
        self._path = overlay_path
        self._logger = logger
        self._proc: Optional[subprocess.Popen] = None

    def running(self) -> bool:
        return self._proc is not None and self._proc.poll() is None

    def _clear_if_exited(self) -> None:
        if self._proc is None:
            return
        rc = self._proc.poll()
        if rc is None:
            return
        self._logger.log(f"overlay exited: rc={rc}")
        self._proc = None

    def start(self) -> None:
        self._clear_if_exited()
        if self.running():
            return
        if not os.path.exists(self._path):
            self._logger.log(f"overlay missing: {self._path}")
            return
        try:
            self._proc = subprocess.Popen([self._path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self._logger.log(f"overlay started: pid={self._proc.pid}")
        except Exception as e:
            self._logger.log(f"failed to start overlay: {e}")
            self._proc = None

    def stop(self, timeout_sec: float = 2.0) -> None:
        self._clear_if_exited()
        if not self.running():
            self._proc = None
            return
        assert self._proc is not None
        try:
            self._logger.log(f"stopping overlay: pid={self._proc.pid}")
            self._proc.terminate()
            self._proc.wait(timeout=timeout_sec)
        except subprocess.TimeoutExpired:
            self._logger.log(f"overlay SIGTERM timeout; killing: pid={self._proc.pid}")
            try:
                self._proc.kill()
                self._proc.wait(timeout=timeout_sec)
            except Exception as e:
                self._logger.log(f"overlay kill failed: {e}")
        except Exception as e:
            self._logger.log(f"overlay stop error: {e}")
        self._proc = None


def _env_int(name: str, default: int) -> int:
    v = os.environ.get(name)
    if not v:
        return default
    try:
        return int(v)
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    v = os.environ.get(name)
    if not v:
        return default
    try:
        return float(v)
    except ValueError:
        return default


def _env_bool(name: str, default: bool) -> bool:
    v = os.environ.get(name)
    if v is None:
        return default
    return v.lower() in ("1", "true", "yes", "on")


def main() -> int:
    _load_config_file(_expand_user_value(os.environ.get("QBS_CONFIG_FILE", "~/.config/quiet-black-screensaver/config.env")))

    state_dir = _state_dir()
    log_path = _expand_user_value(os.environ.get("QBS_LOG_PATH", os.path.join(state_dir, "quiet-black-screensaver.log")))
    lock_path = os.path.join(state_dir, "quiet-black-screensaver.lock")

    logger = Logger(log_path)
    _lock_handle = _acquire_lock(lock_path, logger)

    idle_seconds = max(1, _env_int("QBS_IDLE_SECONDS", 600))
    select_timeout = max(0.2, _env_float("QBS_SELECT_TIMEOUT", 2.0))
    rescan_interval = max(1.0, _env_float("QBS_RESCAN_INTERVAL", 30.0))
    lock_screen = _env_bool("QBS_LOCK_SCREEN", False)

    overlay_path = _expand_user_value(os.environ.get("QBS_OVERLAY_PATH", "~/.local/bin/quiet-black-screen.py"))
    overlay = Overlay(overlay_path, logger)

    enable_pp = _env_bool("QBS_POWER_PROFILE_ENABLE", False)
    pp_profile = os.environ.get("QBS_POWER_PROFILE_ON_BLACK", "power-saver")
    power_tweak = PowerProfileTweak(enable=enable_pp, profile_on_black=pp_profile)

    inhibit_saver = _env_bool("QBS_INHIBIT_SCREENSAVER", True)
    ss_inhibitor = ScreenSaverInhibitor(logger, enabled=(inhibit_saver and not lock_screen))

    stop_flag = {"stop": False}

    def _stop(_signum, _frame) -> None:
        stop_flag["stop"] = True

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)

    monitor = InputMonitor(logger)
    monitor.rescan()
    ss_inhibitor.inhibit()

    last_activity = time.monotonic()
    last_rescan = 0.0

    logger.log(
        "quiet-black-screensaver-daemon started: "
        f"idle={idle_seconds}s timeout={select_timeout}s rescan={rescan_interval}s "
        f"overlay={overlay_path} lock_screen={int(lock_screen)}"
    )

    try:
        while not stop_flag["stop"]:
            now = time.monotonic()

            if now - last_rescan >= rescan_interval:
                added = monitor.rescan()
                last_rescan = now
                if added and not overlay.running():
                    last_activity = time.monotonic()

            active = monitor.wait_activity(select_timeout)
            if active:
                last_activity = time.monotonic()
                if overlay.running():
                    power_tweak.exit(logger)
                    overlay.stop()
                continue

            overlay._clear_if_exited()
            if not overlay.running():
                idle_for = time.monotonic() - last_activity
                if idle_for >= idle_seconds:
                    logger.log(f"idle reached: {idle_for:.1f}s >= {idle_seconds}s; entering black")
                    if lock_screen:
                        subprocess.run(
                            ["qdbus6", "org.freedesktop.ScreenSaver", "/ScreenSaver", "org.freedesktop.ScreenSaver.Lock"],
                            check=False,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )
                        last_activity = time.monotonic()
                    else:
                        power_tweak.enter(logger)
                        overlay.start()
    finally:
        logger.log("daemon stopping; restoring state")
        power_tweak.exit(logger)
        overlay.stop()
        ss_inhibitor.uninhibit()
        monitor.close()

    logger.log("daemon stopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

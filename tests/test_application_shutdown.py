"""The Windows session-end handler must restore the system hotkeys — the
teardown on exec() return does not run when the OS kills a tray app during
shutdown."""
from nexus_kit import Root
from nexus_kit.impl import ContainerInjector

from app.application import Application
from app.config.di import DI_CONFIG
from app.config.environment import Environment
from app.services.system_hotkeys_guard import SystemHotkeysGuard


class FakeGuard:
    def __init__(self):
        self.stop_calls = 0

    def stop(self):
        self.stop_calls += 1


def _application_with_fake_guard():
    env = Environment(Root.external(".env"))
    container = ContainerInjector(DI_CONFIG)
    container.set(Environment, env)
    fake_guard = FakeGuard()
    container.set(SystemHotkeysGuard, fake_guard)
    return Application(env, container), fake_guard


def test_session_end_restores_system_hotkeys():
    app, fake_guard = _application_with_fake_guard()
    app._on_session_end(None)
    assert fake_guard.stop_calls == 1


def test_session_end_is_the_guard_stop_path():
    # A second session-end (or the later teardown) must be safe to call —
    # the guard itself is idempotent, so the Application need not deduplicate.
    app, fake_guard = _application_with_fake_guard()
    app._on_session_end(None)
    app._on_session_end(None)
    assert fake_guard.stop_calls == 2

from injector import inject, singleton

from nexus_kit.interfaces import ServiceInterface

from app.loggers import SystemHotkeysGuardLogger
from engine.interfaces.keyboard_layout_switching_system_settings_interface import \
    KeyboardLayoutSwitchingSystemSettingsInterface


@singleton
class SystemHotkeysGuard(ServiceInterface):
    """Disables the Windows built-in layout-switch hotkeys for the app's
    lifetime and restores them on exit — via ServiceRunner teardown on a
    clean quit, and via the Application's session-end handler on Windows
    shutdown/logoff. A hard kill (power loss, force-close) can't restore in
    the moment, but the originals are backed up to disk, so the next run —
    or the next clean quit — recovers them (see
    WindowsKeyboardLayoutSwitchingSettings)."""

    @inject
    def __init__(
            self,
            system_settings: KeyboardLayoutSwitchingSystemSettingsInterface,
            log: SystemHotkeysGuardLogger,
    ):
        self._system_settings = system_settings
        self._log = log
        self._disabled = False

    def start(self):
        self._system_settings.disable_system_hotkeys()
        self._disabled = True
        self._log.info("system layout hotkeys disabled")

    def stop(self):
        if not self._disabled:
            return

        self._system_settings.restore_system_hotkeys()
        self._disabled = False
        self._log.info("system layout hotkeys restored")

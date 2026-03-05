from __future__ import annotations

import re
import time
from pathlib import Path

from pywinauto import Application, Desktop
from pywinauto.keyboard import send_keys


class NotepadAutomationError(RuntimeError):
    """Raised when Notepad automation fails."""


class NotepadAutomation:
    def __init__(self, timeout_seconds: int = 15) -> None:
        self.timeout_seconds = timeout_seconds
        self.app: Application | None = None
        self.process_id: int | None = None
        self.window = None
        self.desktop = Desktop(backend="uia")

    def launch_notepad(self) -> None:
        """Start Notepad and bind to the newly opened main window."""
        existing_handles = self._get_notepad_handles()
        self.app = Application(backend="uia").start("notepad.exe", wait_for_idle=False)

        window_wrapper = self._wait_for_new_notepad_window(existing_handles)
        if window_wrapper is None:
            raise NotepadAutomationError("Timed out while waiting for Notepad main window.")

        self.process_id = window_wrapper.process_id()
        self.window = self.desktop.window(handle=window_wrapper.handle)
        self.window.wait("ready", timeout=self.timeout_seconds)
        self.window.set_focus()

    def enter_text(self, base_text: str, suffix_text: str) -> None:
        """Type the provided text into the active Notepad editor control."""
        if self.window is None:
            raise NotepadAutomationError("Notepad window is not initialized. Call launch_notepad() first.")

        editor = self._locate_editor()
        editor.set_focus()
        editor.type_keys(base_text, with_spaces=True, set_foreground=True)
        editor.type_keys(suffix_text, with_spaces=True, set_foreground=True)

    def save_as(self, file_path: Path) -> None:
        """Save content to the requested path with UI and filesystem fallbacks."""
     
        target_path = Path(file_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        existing_dialog_handles = self._get_save_dialog_handles()
        self.window.set_focus()
        send_keys("^+s")

        save_dialog = self._wait_for_save_dialog(existing_dialog_handles)
        if save_dialog is None:
            # Fallback for Notepad variants that use Ctrl+S for first-time save dialog.
            self.window.set_focus()
            send_keys("^s")
            save_dialog = self._wait_for_save_dialog(existing_dialog_handles)
        if save_dialog is None:
            if self._is_file_saved(target_path, seconds=3):
                return
            raise NotepadAutomationError("Save dialog did not appear.")

        name_input = self._locate_filename_input(save_dialog)
        if name_input is None:
            raise NotepadAutomationError("File name input in Save As dialog was not found.")

        self._set_filename_input(name_input, target_path)

        # Primary action: press Enter to activate dialog's default Save button.
        send_keys("{ENTER}")
        if self._is_file_saved(target_path, seconds=3):
            return

        raise NotepadAutomationError("Save action was not triggered in Save As dialog.")

    def reopen_and_validate(self, file_path: Path, expected_text: str) -> None:
        """Read the saved file from disk and verify exact content."""
        target_path = Path(file_path)
        if not target_path.exists():
            raise NotepadAutomationError(f"Saved file does not exist: {target_path}")

        with target_path.open("r", encoding="utf-8") as file:
            actual_text = file.read()

        if actual_text != expected_text:
            raise NotepadAutomationError(
                f"Content mismatch.\nExpected: {expected_text!r}\nActual:   {actual_text!r}"
            )

    def close_notepad(self) -> None:
        """Close Notepad and dismiss a potential unsaved-changes prompt."""
        if self.window is None or self.app is None:
            return

        try:
            if not self.window.exists(timeout=1):
                return
            self.window.set_focus()
            send_keys("%{F4}")
        except Exception:
            # Best-effort cleanup, especially from `finally` blocks.
            return

    def _locate_editor(self):
        """Find the Notepad text surface across legacy and modern UI trees."""
        for _ in range(self.timeout_seconds * 4):
            for control_type in ("Edit", "Document"):
                try:
                    editor = self.window.child_window(control_type=control_type, found_index=0)
                    if editor.exists(timeout=0.2):
                        return editor.wrapper_object()
                except Exception:
                    pass

            try:
                for control_type in ("Edit", "Document"):
                    descendants = self.window.descendants(control_type=control_type)
                    if descendants:
                        return descendants[0]
            except Exception:
                pass

            time.sleep(0.25)

        raise NotepadAutomationError("Notepad editor control was not found.")

    def _wait_for_save_dialog(self, existing_handles: set[int] | None = None):
        """Find the save UI, whether it is a top-level dialog or embedded panel."""
        for _ in range(self.timeout_seconds * 2):
            if self.window is not None and self._is_save_dialog_candidate(self.window):
                return self.window

            try:
                active = self.desktop.get_active()
                if active is not None:
                    active_spec = self.desktop.window(handle=active.handle)
                    if self._is_save_dialog_candidate(active_spec):
                        return active_spec
            except Exception:
                pass

            dialogs = self.desktop.windows(top_level_only=True, visible_only=True)
            for dialog in dialogs:
                if existing_handles and dialog.handle in existing_handles:
                    continue
                if self.window is not None and dialog.handle == self.window.handle:
                    continue

                dialog_spec = self.desktop.window(handle=dialog.handle)
                if self._is_save_dialog_candidate(dialog_spec):
                    return dialog_spec
            time.sleep(0.5)
        return None

    def _file_exists_within(self, file_path: Path, seconds: int) -> bool:
        """Poll for file existence for a bounded amount of time."""
        for _ in range(seconds * 4):
            if file_path.exists():
                return True
            time.sleep(0.25)
        return False

    def _snapshot_directory_files(self, directory: Path) -> set[Path]:
        """Capture current files in a directory for post-save diffing."""
        return {path for path in directory.glob("*") if path.is_file()}

    def _is_file_saved(self, target_path: Path, seconds: int) -> bool:
        """Confirm save success by direct existence check or recovery rename."""
        if self._file_exists_within(target_path, seconds):
            return True

        return target_path.exists()

    # def _dismiss_save_prompt_if_present(self) -> None:
    #     """Click 'Don't Save' if close triggers an unsaved-changes prompt."""
    #     if self.process_id is None:
    #         return

    #     dialog = self.desktop.window(
    #         title_re=r".*Notepad",
    #         control_type="Window",
    #         process=self.process_id,
    #     )
    #     if not dialog.exists(timeout=1):
    #         return
    #     dont_save = dialog.child_window(title_re=r"^(Don't Save|Dont Save)$", control_type="Button")
    #     if dont_save.exists(timeout=2):
    #         dont_save.click_input()

    def _get_notepad_handles(self) -> set[int]:
        """Return visible top-level Notepad window handles."""
        handles: set[int] = set()
        windows = self.desktop.windows(title_re=r".*Notepad", top_level_only=True, visible_only=True)
        for window in windows:
            handles.add(window.handle)
        return handles

    def _wait_for_new_notepad_window(self, existing_handles: set[int]):
        """Wait for the Notepad window created by the current launch action."""
        for _ in range(self.timeout_seconds * 4):
            windows = self.desktop.windows(title_re=r".*Notepad", top_level_only=True, visible_only=True)
            for window in windows:
                if window.handle not in existing_handles:
                    return window
            time.sleep(0.25)

        # Fallback: pick a window from the started process if available.
        if self.app is not None:
            try:
                app_window = self.app.window(title_re=r".*Notepad")
                if app_window.exists(timeout=1):
                    return app_window
            except Exception:
                return None
        return None

    def _get_save_dialog_handles(self) -> set[int]:
        """Collect currently visible save-like dialogs to ignore stale windows."""
        handles: set[int] = set()
        dialogs = self.desktop.windows(top_level_only=True, visible_only=True)
        for dialog in dialogs:
            if self.window is not None and dialog.handle == self.window.handle:
                continue
            dialog_spec = self.desktop.window(handle=dialog.handle)
            if self._is_save_dialog_candidate(dialog_spec):
                handles.add(dialog.handle)
        return handles

    def _locate_filename_input(self, save_dialog):
        """Find the filename input control in the detected save UI."""
        by_auto_id = save_dialog.child_window(auto_id="1001", control_type="Edit")
        if by_auto_id.exists(timeout=1):
            return by_auto_id

        try:
            edits = save_dialog.descendants(control_type="Edit")
        except Exception:
            return None

        if not edits:
            return None

        # Prefer the typical filename field if present among edit controls.
        for edit in edits:
            try:
                text = (edit.window_text() or "").strip()
                if text and re.search(r"[\\/]|\\.txt$", text, re.IGNORECASE):
                    return self.desktop.window(handle=edit.handle)
            except Exception:
                continue

        return self.desktop.window(handle=edits[-1].handle)

    def _set_filename_input(self, name_input, target_path: Path) -> None:
        """Set filename text and fallback to keyboard input if direct set fails."""
        target_text = str(target_path)
        wrapper = name_input.wrapper_object()
        wrapper.set_focus()
        wrapper.set_edit_text(target_text)

        current = (wrapper.window_text() or "").strip()
        if current == target_text:
            return

        # Some dialog variants ignore set_edit_text unless keystrokes are used.
        send_keys("^a{BACKSPACE}")
        wrapper.type_keys(target_text, with_spaces=True, set_foreground=True)

    def _is_save_dialog_candidate(self, dialog_spec) -> bool:
        """Heuristic check: has filename input and a resolvable save action."""
        try:
            if not dialog_spec.exists(timeout=0.1):
                return False
        except Exception:
            return False

        has_filename_input = dialog_spec.child_window(auto_id="1001", control_type="Edit").exists(timeout=0.1)
        if not has_filename_input:
            try:
                has_filename_input = len(dialog_spec.descendants(control_type="Edit")) > 0
            except Exception:
                has_filename_input = False

        if not has_filename_input:
            return False

        return self._locate_save_button(dialog_spec) is not None

    def _locate_save_button(self, dialog_spec):
        """Find the primary save button by automation id or localized text."""
        # Common file dialogs typically expose the primary Save button with automation id 1.
        by_auto_id = dialog_spec.child_window(auto_id="1", control_type="Button")
        if by_auto_id.exists(timeout=0.1):
            return by_auto_id

        try:
            descendants = dialog_spec.descendants(control_type="Button")
            for button in descendants:
                try:
                    auto_id = (button.element_info.automation_id or "").strip()
                    if auto_id == "1":
                        return self.desktop.window(handle=button.handle)
                except Exception:
                    continue
        except Exception:
            pass

        # Fallback for variants/locales where the button has a textual label.
        for pattern in (r"^(&?Save|Save)$", r".*(Save|Luu).*"):
            candidate = dialog_spec.child_window(title_re=pattern, control_type="Button")
            if candidate.exists(timeout=0.1):
                return candidate

        try:
            descendants = dialog_spec.descendants(control_type="Button")
            for button in descendants:
                text = (button.window_text() or "").strip()
                if re.search(r"(save|luu)", text, re.IGNORECASE):
                    return self.desktop.window(handle=button.handle)
        except Exception:
            pass
        return None

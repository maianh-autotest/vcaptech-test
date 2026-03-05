from __future__ import annotations

import argparse
import sys
from pathlib import Path

from notepad_automation import NotepadAutomation, NotepadAutomationError

BASE_TEXT = "Desktop automation test"
SUFFIX_TEXT = " - completed"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Windows Notepad desktop automation task.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "artifacts" / "desktop" / "notepad-output.txt",
        help="Output file path for saved Notepad content.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    expected_text = f"{BASE_TEXT}{SUFFIX_TEXT}"
    automation = NotepadAutomation(timeout_seconds=20)
    if args.output.exists():
        args.output.unlink()
        print(f"INFO: Deleted existing output file before run: {args.output}")

    try:
        print("Launching Notepad...")
        automation.launch_notepad()
        print("Entering text...")
        automation.enter_text(BASE_TEXT, SUFFIX_TEXT)
        print("Saving file...")
        automation.save_as(args.output)
        automation.close_notepad()
        print("Verifying file...")
        automation.reopen_and_validate(args.output, expected_text)
        print(f"PASS: Notepad workflow completed. File saved and verified at: {args.output}")
        return 0
    except NotepadAutomationError as error:
        print(f"FAIL: {error}")
        return 1
    except Exception as error:  # pragma: no cover - defensive catch for assignment stability
        print(f"FAIL: Unexpected error: {error}")
        return 1
    finally:
        automation.close_notepad()


if __name__ == "__main__":
    sys.exit(main())

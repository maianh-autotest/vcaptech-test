# VCapTech Automation Home Assignment

This repository contains a hybrid implementation for the assignment:

- Task 1 Desktop automation: Python + `pywinauto`
- Task 2 Web automation: Playwright + TypeScript
- Task 2B Bonus API thinking: Playwright API request test (optional runtime)

## Project Structure

- `desktop-tests/` Desktop automation code for Windows Notepad
- `web-tests/` Playwright web and API tests
- `artifacts/` Output files, screenshots, and report artifacts

## Prerequisites

- Windows OS (for Notepad automation)
- Python 3.10+ and `pip`
- Node.js 20+ and `npm`

## Setup

### Desktop test setup

```powershell
cd desktop-tests
pip install -r requirements.txt
```

### Web test setup

```powershell
cd web-tests
npm install
npx playwright install
```

## Run Tests

### Task 1: Desktop Notepad automation

From repository root:

```powershell
python desktop-tests/main.py
```

This will:

1. Launch Notepad
2. Type `Desktop automation test`
3. Append ` - completed`
4. Save file to `artifacts/desktop/notepad-output.txt`
5. Reopen and verify file content (bonus)

### Task 2: Web RocPortal login navigation

From repository root:

```powershell
cd web-tests
npm run test
```

Assertions include:

- URL is `https://auth.rocscience.com/u/login`
- Email input visible
- Password input visible
- Login button visible and enabled

### Task 2b Answer

Task 2b answer is documented at:

- `web-tests\task2b.md`

## Evidence of Execution

- Desktop output file: `artifacts/desktop/notepad-output.txt`
- Playwright HTML report: `artifacts/playwright-report/`
- Test result traces/screenshots (on failure): `artifacts/test-results/`

You can also add manual screenshots to:

- `artifacts/screenshots/desktop/`
- `artifacts/screenshots/web/`

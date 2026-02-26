
---

## M4.2 – Configuration Centralization (Step 1-2)

### Objective
Introduce centralized configuration defaults without changing runtime behavior.

### Changes Introduced
- Added `apps/config.py`
- Centralized:
  - IPC host default
  - IPC port default
  - Serial timeout default
  - Serial baud default
- Updated `SerialDaemon` to use configuration constants instead of hardcoded literals.

### Impact
- No functional changes.
- No behavioral regression.
- Provides foundation for future timeout and retry strategy.

### Status
Completed (conservative implementation).

# SPE Web Terminal 2 — Project TODO

This file tracks short-term development tasks.

The project follows an incremental milestone strategy focused on reliability and stability.

---

# Current Milestone

Milestone 4.2 — Transaction Timeout Strategy

Branch: `milestone-4.2`

Goal:

Introduce a safe framework for transaction-aware retry and timeout handling in the serial daemon.

Important rule:

Default behaviour must remain unchanged unless explicitly enabled.

---

# Completed Recently

- Stabilized `apps/seriald.py`
- Restored clean serial daemon implementation
- Introduced transaction retry framework structure
- Default retry count set to **0** (no behaviour change)
- Added Windows development launcher (`dev/run_win.ps1`)
- Repository cleanup and `.gitignore` stabilization
- Documentation alignment for new development sessions

---

# Next Tasks

Serial layer improvements:

- Implement transaction-aware timeout handling
- Improve retry/backoff policy
- Extend structured error metadata
- Improve diagnostic logging

Testing:

- Serial failure simulation
- Timeout handling validation
- IPC stress validation

---

# Later Tasks

Future improvements planned after Milestone 4 completion:

- Protocol layer stabilization
- Amplifier state synchronization
- Web interface integration
- Production hardening

---

# Notes

All development must follow the project philosophy:

- minimal dependencies
- conservative modifications
- no unnecessary refactoring
- test before commit
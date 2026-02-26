# Project TODO

This TODO is intentionally short and milestone-driven.
Restore point: tag `m4.1-tested`.

---

## Done
- [x] M4.1: Structured SerialError model
- [x] M4.1: ErrorStore ring buffer
- [x] M4.1: Record at least one real serial error path (serial_write_failed)
- [x] M4.1: Unit tests (SerialError + ErrorStore)
- [x] M4.1: Integration smoke test (daemon boots + IPC ping)
- [x] M4.1: IPC stress script (1000 sequential ping requests, 0 errors)

---

## Next (Milestone 4.2) — Timeout & retry policy
- [ ] Define a single source of truth for timeouts (IPC + serial)
- [ ] Standardize timeout error mapping (ipc_timeout vs serial timeout)
- [ ] Add minimal retry policy for idempotent operations only (max 1 retry)
- [ ] Add integration test(s) for timeout behavior (virtual / harness)

---

## Next (Milestone 4.3) — Edge-case test harness (virtual/loopback)
- [ ] Document a repeatable loopback setup (COM0COM on Windows; equivalent notes for Linux/macOS)
- [ ] Add at least 3 reproducible test cases (timeout, partial frame, port disappears)
- [ ] Validate that last/recent errors reflect expected layer/kind/op

---

## Mid term
- [ ] Extend serial command coverage (incremental, hardware-safe)
- [ ] Improve HTTP API documentation (OpenAPI + examples)
- [ ] Optional config file support (keep env vars as primary)

---

## Long term
- [ ] Web-based user interface (optional)
- [ ] Hardware-specific profiles (optional)
- [ ] Optional authentication layer (only if remote exposure becomes a requirement)

---

### Completed in M4.2
- Centralized IPC and Serial default configuration (no behavior change)
- Added unit tests for configuration defaults

# Project Milestones — SPE Web Terminal 2

This file describes the major development phases of the project.

Milestones correspond to tagged stable states in the repository.

Current stable baseline:
m4.1-tested

---

# M1 — IPC baseline

Tag: m1-closed

Goal:
Establish the first working internal architecture between components.

Key elements introduced:
- IPC communication layer
- basic daemon structure
- status and metrics reporting
- minimal HTTP exposure

Outcome:
A working internal communication backbone between services.

Status:
DONE

---

# M2 — Serial integration

Tag: m2-closed

Goal:
Introduce real serial device interaction with configuration via environment variables.

Key elements introduced:
- serial port probing
- environment-based serial configuration
- initial serial daemon integration

Outcome:
The system can communicate with the amplifier through the serial interface.

Status:
DONE

---

# M3 — Operational API surface

Tag: m3-closed

Goal:
Expose operational capabilities through the HTTP interface and stabilize runtime behavior.

Key elements introduced:
- HTTP endpoints for diagnostics and status
- serial operations (open / close / write / recent)
- runtime logging and debugging helpers
- repository cleanup and documentation improvements

Outcome:
A usable operational backend capable of controlling and observing the amplifier.

Status:
DONE

---

# M4 — Reliability and configuration architecture

Current milestone.

Focus areas:
- structured error reporting
- timeout handling
- configuration centralization
- reliability improvements

Baseline tag:
m4.1-tested

Completed steps:
- structured SerialError model
- ErrorStore ring buffer
- configuration centralization (apps/config.py)
- serial transaction defaults
- repository hygiene improvements
- documentation updates

Current branch:
milestone-4.2

Next goals:
- timeout mapping across layers
- retry policy for idempotent operations
- integration tests for timeout behaviour

Status:
IN PROGRESS
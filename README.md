# SPE Web Terminal 2

SPE Web Terminal 2 is an independent open-source backend providing a local HTTP interface
for monitoring and controlling SPE Expert linear amplifiers.

This project is NOT affiliated with, endorsed by, or supported by SPE.

The focus is on:
- reliability
- clear architecture
- minimal dependencies
- cross-platform behavior (Windows, macOS, Linux)
- incremental development without over-engineering

---

# Project Status

Current stable baseline tag:

- m4.1-tested — unified error model + unit tests + integration smoke + IPC stress validated

Development follows incremental milestones.
See Milestone_4_Spec_SPE_Web_Terminal_2.md for details.

---

# Architecture

The system is composed of three main components:

HTTP Service  <---->  IPC Layer  <---->  Serial Daemon  <---->  Amplifier

1. HTTP Service  
   Exposes REST endpoints for status, metrics, and control.

2. Serial Daemon  
   Handles low-level serial I/O (RS-232 / USB-VCP).  
   Maintains runtime metrics and structured error reporting.

3. IPC Layer  
   Internal TCP-based communication between HTTP service and daemon.  
   Prevents HTTP blocking due to serial failures.

---

# Installation

## Requirements

- Python 3.11+
- Windows, macOS or Linux
- Virtual environment recommended

## Setup

Clone the repository:

git clone <repository-url>
cd SPEWebTerminal2

Create virtual environment:

python -m venv .venv

Activate (Windows / Git Bash):

source .venv/Scripts/activate

Install dependencies:

pip install -r requirements.txt
pip install pytest

---

# Running the Serial Daemon

From project root:

python -m apps.seriald

Default IPC configuration:
- Host: 127.0.0.1
- Port: 8765

Serial configuration can be provided via environment variables:

SPE_SERIAL_PORT=COM16
SPE_SERIAL_BAUD=115200

---

# Testing

## Unit Tests

python -m pytest tests/unit

## Integration Smoke Test

python -m pytest tests/integration/test_seriald_ipc.py

## IPC Stress Test (manual)

python tests/integration/stress_ipc_ping.py

Expected result:
- 1000 ping requests
- Errors: 0

---

# Error Model

Milestone 4 introduces:

- Structured SerialError
- In-memory ErrorStore
- Unified serial-layer error reporting

Errors are:
- timestamped (UTC ISO-8601)
- JSON serializable
- bounded in size
- safe for diagnostics

---

# Development Philosophy

- No premature abstraction
- No unnecessary frameworks
- Conservative refactors
- Feature gating by milestone
- Tests before feature expansion

Tags are used as recovery anchors.

---

# License

MIT License — see LICENSE file for details.

Copyright (c) 2026 Melox97

---

# Configuration

Environment variables:

- SPE_SERIAL_PORT – Serial device path (e.g. COM3, /dev/ttyUSB0)
- SPE_SERIAL_BAUD – Serial baud rate (default: 115200)


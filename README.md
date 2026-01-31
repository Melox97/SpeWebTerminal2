# SPE Web Terminal 2

SPE Web Terminal 2 is an **independent and open-source project** that provides a
local HTTP backend for monitoring and controlling SPE Expert linear amplifiers.

This project is **not affiliated with, endorsed by, or supported by SPE**.
It is developed as a community-driven initiative with a focus on simplicity,
stability, and portability.

## Overview

The application exposes a minimal HTTP API and delegates all serial communication
to a dedicated backend component.  
The architecture is intentionally simple and designed to run on common platforms
such as Windows, macOS, and Linux.

Key goals:
- clear separation of concerns
- predictable behavior
- minimal dependencies
- local-first operation

## Architecture

The system is composed of three main parts:

- **HTTP Service**  
  Exposes REST endpoints for status, metrics, and control.

- **Serial Daemon**  
  Handles low-level serial I/O with the amplifier (RS-232 / USB-VCP).

- **IPC Layer**  
  Internal communication channel between HTTP service and serial daemon.

This separation allows the HTTP layer to remain responsive even when the serial
interface is unavailable or misconfigured.

## Logging and diagnostics

The application maintains **local runtime logs** for troubleshooting purposes.

An optional debug endpoint allows generating **snapshot log files** that capture
the current runtime state.  
Snapshots are saved locally and are **not intended to be versioned or shared**.

The log directory is intentionally excluded from version control.

## Project status

The project is under active development and currently focuses on:

- backend stability
- serial communication reliability
- cross-platform behavior consistency

User interfaces, advanced control logic, and hardware-specific features will be
introduced incrementally.

## License

This project is released under an open-source license.  
See the `LICENSE` file for details.

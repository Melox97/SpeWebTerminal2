"""
Centralized configuration defaults for SPE Web Terminal 2.

Milestone 4.2 introduces timeout standardization.
Keep values aligned with current behavior unless explicitly changed.
"""

# IPC defaults
IPC_HOST_DEFAULT = "127.0.0.1"
IPC_PORT_DEFAULT = 8765
IPC_TIMEOUT_S_DEFAULT = 1.5  # reserved for future IPC client usage

# Serial defaults
SERIAL_TIMEOUT_S_DEFAULT = 0.2  # matches current seriald behavior
SERIAL_BAUD_DEFAULT = 115200
from apps.config import (
    IPC_HOST_DEFAULT,
    IPC_PORT_DEFAULT,
    IPC_TIMEOUT_S_DEFAULT,
    SERIAL_TIMEOUT_S_DEFAULT,
    SERIAL_BAUD_DEFAULT,
    SERIAL_TXN_TIMEOUT_S_DEFAULT,
    SERIAL_TXN_RETRIES_DEFAULT,
    SERIAL_RETRY_BACKOFF_S_DEFAULT,
)

def test_config_defaults_exist_and_types():
    assert isinstance(IPC_HOST_DEFAULT, str)
    assert isinstance(IPC_PORT_DEFAULT, int)
    assert isinstance(IPC_TIMEOUT_S_DEFAULT, (int, float))
    assert isinstance(SERIAL_TIMEOUT_S_DEFAULT, (int, float))
    assert isinstance(SERIAL_BAUD_DEFAULT, int)
    assert isinstance(SERIAL_TXN_TIMEOUT_S_DEFAULT, (int, float))
    assert isinstance(SERIAL_TXN_RETRIES_DEFAULT, int)
    assert isinstance(SERIAL_RETRY_BACKOFF_S_DEFAULT, (int, float))


def test_config_defaults_expected_values():
    assert IPC_HOST_DEFAULT == "127.0.0.1"
    assert IPC_PORT_DEFAULT == 8765
    assert SERIAL_BAUD_DEFAULT == 115200
    # conservative: must remain aligned with current seriald behavior
    assert SERIAL_TIMEOUT_S_DEFAULT == 0.2
    assert SERIAL_TXN_TIMEOUT_S_DEFAULT == SERIAL_TIMEOUT_S_DEFAULT
    assert SERIAL_TXN_RETRIES_DEFAULT == 0
    assert SERIAL_RETRY_BACKOFF_S_DEFAULT == 0.05


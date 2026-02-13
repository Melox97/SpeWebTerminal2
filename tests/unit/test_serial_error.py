import re

from apps.serial_error import bytes_to_hex_limited, make_serial_error


_TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def test_make_serial_error_minimal_fields():
    e = make_serial_error(layer="serial", kind="timeout", op="status", retryable=True)
    assert e["layer"] == "serial"
    assert e["kind"] == "timeout"
    assert e["op"] == "status"
    assert e["retryable"] is True
    assert "ts" in e
    assert _TS_RE.match(e["ts"])


def test_make_serial_error_truncates_hex_fields():
    long_hex = "a" * 600  # > 512
    e = make_serial_error(
        layer="serial",
        kind="port_error",
        op="serial_write",
        retryable=True,
        tx_hex=long_hex,
        rx_hex=long_hex,
    )
    assert len(e["tx_hex"]) == 512
    assert len(e["rx_hex"]) == 512


def test_bytes_to_hex_limited_none():
    assert bytes_to_hex_limited(None) is None


def test_bytes_to_hex_limited_truncates():
    data = bytes(range(256)) + bytes(range(256))  # 512 bytes
    hx = bytes_to_hex_limited(data, max_bytes=10)
    assert hx == data[:10].hex()
    assert len(hx) == 20  # 10 bytes -> 20 hex chars


def test_bytes_to_hex_limited_zero_max():
    data = b"\x01\x02\x03"
    hx = bytes_to_hex_limited(data, max_bytes=0)
    assert hx == ""

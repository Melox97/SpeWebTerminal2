from datetime import datetime, timezone
from typing import NotRequired, TypedDict


class SerialError(TypedDict):
    ts: str
    layer: str
    kind: str
    op: str
    retryable: bool
    port: NotRequired[str]
    baud: NotRequired[int]
    timeout_s: NotRequired[float]
    tx_hex: NotRequired[str]
    rx_hex: NotRequired[str]
    detail: NotRequired[str]
    correlation_id: NotRequired[str]


def bytes_to_hex_limited(data: bytes | None, max_bytes: int = 256) -> str | None:
    if data is None:
        return None
    if max_bytes <= 0:
        return ""
    return data[:max_bytes].hex()


def make_serial_error(
    layer: str,
    kind: str,
    op: str,
    retryable: bool,
    *,
    port: str | None = None,
    baud: int | None = None,
    timeout_s: float | None = None,
    tx_hex: str | None = None,
    rx_hex: str | None = None,
    detail: str | None = None,
    correlation_id: str | None = None,
) -> SerialError:
    err: SerialError = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "layer": layer,
        "kind": kind,
        "op": op,
        "retryable": retryable,
    }
    if port is not None:
        err["port"] = port
    if baud is not None:
        err["baud"] = baud
    if timeout_s is not None:
        err["timeout_s"] = timeout_s
    if tx_hex is not None:
        err["tx_hex"] = tx_hex[:512]
    if rx_hex is not None:
        err["rx_hex"] = rx_hex[:512]
    if detail is not None:
        err["detail"] = detail
    if correlation_id is not None:
        err["correlation_id"] = correlation_id
    return err

